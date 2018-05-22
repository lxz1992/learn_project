'''
Created on Jan 18, 2018

@author: MTK06979
'''
import datetime
import json
import math
import os
import re
import subprocess
from subprocess import PIPE


class Build:
    ALPHA = "alpha"
    BETA = "beta"
    RC = "rc"
    # won't use >
    RTM = "rtm"
    GA = "ga"
    # < won't use
    GOLD = "gold"


class FrontendSys:
    CR = "cr_review_sys"
    MD = "md_analysis"


class PodFile:
    blue = "pod-blue.json"
    green = "pod-green.json"
    pod = "pod.json"


def __get_frontend_setting():
    my_todo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    setting = os.path.join(
        my_todo_root, "frontend", "package.json")
    return setting


def __get_frontend_version():
    setting = __get_frontend_setting()
    target_ver = "0.0.1"
    with open(setting, 'r', encoding="UTF-8") as f:
        setting_obj = json.load(f)
        target_ver = setting_obj["version"]

    print(target_ver)

    return target_ver


def __get_backend_setting():
    my_todo_app = os.path.dirname(os.path.dirname(__file__))
    my_todo_setting = os.path.join(my_todo_app, "settings_dev.py")
    return my_todo_setting


def __get_jenkinsfile():
    my_todo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    jenkins_file = os.path.join(my_todo_root, "Jenkinsfile")
    return jenkins_file


def __get_config_dir():
    my_todo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(my_todo_root, "config")


def __get_deploy_pod(deploy_pod):
    pod_file = os.path.join(__get_config_dir(), "deploy", deploy_pod)
    return pod_file


def __get_ha_pod(deploy_pod):
    pod_file = os.path.join(__get_config_dir(), "haproxy", deploy_pod)
    return pod_file


def __get_ngix_pod(deploy_pod):
    pod_file = os.path.join(__get_config_dir(), "nginx", deploy_pod)
    return pod_file


def __gen_frontend_verion(v):
    m = re.search("(?P<M>\d+)\.(?P<m>\d+)\.(?P<build>\d+)", v)
    new_v = v
    if m:
        old_build = int(m.group("build")) + 1
        build = (old_build) % 10
        minor = int(m.group('m'))
        minor += math.floor(old_build / 10)

        # major is controlled by human
        new_v = "{}.{}.{}".format(m.group("M"), minor, build)

    print(new_v)

    return new_v


def __update_frontend_version(ver):
    setting = __get_frontend_setting()
    with open(setting, 'r+', encoding="UTF-8") as f:
        setting_obj = json.load(f)
        setting_obj["version"] = ver
        f.seek(0)
        json.dump(setting_obj, f, indent=2)


def __exeCmd(cmd, **kwds):
    #     cwd = kwds.get("cwd", os.path.dirname(
    #         os.path.dirname(os.path.dirname(__file__))))
    #     print(cwd)
    p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    if not p.returncode:
        print(out)
        print(err)
    else:
        raise Exception(err, out)


def stash_save():
    __exeCmd(["git", "add", "-u", "."])
    __exeCmd(["git", "stash", "save"])


def get_version():
    # get backend version
    backend_ver = "{}-alpha1".format(
        datetime.datetime.now().strftime("%Y%m%d"))
    my_todo_setting = __get_backend_setting()
    with open(my_todo_setting, 'r')as f:
        setting = f.read()
        m = re.search(
            "^BACKEND_VERSION\s*=\s*\"(?P<backend_ver>.*)\"\s*\n", setting, re.MULTILINE)
        if m:
            backend_ver = m.group("backend_ver")

    print(backend_ver)

    frontend_version = __get_frontend_version()

    return (backend_ver, frontend_version)


def generate_release_version(backend_ver, frontend_version):
    new_backend_ver = backend_ver

    m = re.search("(?P<date>\d+)\-(?P<phase>[a-zA-Z]+)(?P<build>\d+)", backend_ver)
    if m:
        build = int(m.group("build"))
        build += 1

        # phase is controlled by human
        new_backend_ver = "{}-{}{}".format(
            datetime.datetime.now().strftime("%Y%m%d"), m.group("phase"), build)

    print(new_backend_ver)

    new_frontend_version = __gen_frontend_verion(frontend_version)

    return (new_backend_ver, new_frontend_version)


def __update_backend(file_path, pattern, repl):
    setting_file = file_path
    with open(setting_file, 'r+', encoding="UTF-8") as f:
        setting = f.read()
        new_setting = re.sub(pattern,
                             repl, setting, flags=re.MULTILINE)
        f.seek(0)
        f.write(new_setting)


def update_version(backend_ver, frontend_version):

    # update settings
    bk_version_string = 'BACKEND_VERSION = "{}"\n\n'.format(backend_ver)
    __update_backend(__get_backend_setting(),
                     "^BACKEND_VERSION\s*=\s*\"(?P<backend_ver>.*)\"\s*", bk_version_string)

    # update jenkins file
    bk_version_string = 'def tagName = "{}"'.format(backend_ver)
    __update_backend(__get_jenkinsfile(),
                     "^def tagName = \"\S+\"", bk_version_string)

    # update pods
    bk_version_string = '"image": "172.27.16.100:5000/mytodoprod_haproxy1:{}",'.format(
        backend_ver)
    __update_backend(__get_ha_pod(PodFile.pod),
                     '\"image\": \S+mytodoprod_\S+:\S+\",', bk_version_string)

    bk_version_string = '"image": "172.27.16.100:5000/mytodoprod_app1:{}",'.format(
        backend_ver)
    __update_backend(__get_deploy_pod(PodFile.blue),
                     '\"image\": \S+mytodoprod_\S+:\S+\",', bk_version_string)

    bk_version_string = '"image": "172.27.16.100:5000/mytodoprod_app1:{}",'.format(
        backend_ver)
    __update_backend(__get_deploy_pod(PodFile.green),
                     '\"image\": \S+mytodoprod_\S+:\S+\",', bk_version_string)

    bk_version_string = '"image": "172.27.16.100:5000/mytodoprod_nginx1:{}",'.format(
        backend_ver)
    __update_backend(__get_ngix_pod(PodFile.blue),
                     '\"image\": \S+mytodoprod_\S+:\S+\",', bk_version_string)

    bk_version_string = '"image": "172.27.16.100:5000/mytodoprod_nginx1:{}",'.format(
        backend_ver)
    __update_backend(__get_ngix_pod(PodFile.green),
                     '\"image\": \S+mytodoprod_\S+:\S+\",', bk_version_string)

    # frontend
    __update_frontend_version(frontend_version)


def commit(version):
    __exeCmd(["git", "add", "-u", "."])
    __exeCmd(["git", "commit", "-m", '[release] prepare for {}'.format(version)])


def generate_release_commit():
    stash_save()
    versions = get_version()
    new_versions = generate_release_version(*versions)
    update_version(*new_versions)
    commit(new_versions[0])


if __name__ == '__main__':
    generate_release_commit()
