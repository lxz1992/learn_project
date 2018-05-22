'''
Created on Sep 21, 2017

@author: mtk06979
'''
from datetime import datetime
import getpass
import os

from fabric.api import lcd, local
from fabric.colors import green
from fabric.context_managers import shell_env
from fabric.main import main


proj_dir = os.path.dirname(os.path.abspath(__file__))
frontend = os.path.join(proj_dir, 'frontend')

proxy = 'http://172.23.29.23:3128'
user_local_build_cmd = "echo skip_yarn"
set_proxy = 'npm config set proxy {}'.format(proxy)


cur_user = getpass.getuser()
if cur_user.lower().startswith("mtk"):
    user_local_build_cmd = "npm install -g yarn"
    set_proxy = "echo skip_proxy"

os.environ.setdefault('WORKSPACE', os.getcwd())
os.environ.setdefault(
    'BUILD_NUMBER', datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))


def __showMessge(color, msg):
    print(color(msg))


def install_frontend():
    with lcd(frontend):
        __showMessge(green, "working on {} ...".format(os.getcwd()))
        local('{} && {} && yarn install '.format(
            set_proxy, user_local_build_cmd))


def build_frontend(mode="prod"):
    with lcd(frontend):
        __showMessge(green, "working on {} ...".format(os.getcwd()))
        local('npm run prebuild-prod && npm run build-{}'.format(mode))

def run_django_collect_static():
    with lcd(proj_dir):
        __showMessge(green, "working on {} ...".format(os.getcwd()))
        local('python manage.py collectstatic --noinput')


def run_django_test(boxed=""):
    with lcd(proj_dir):
        __showMessge(green, "working on {} ...".format(os.getcwd()))
        report_dir = os.path.join(os.environ['WORKSPACE'], "test_report")
        output_path = os.path.join(report_dir, "test_result_{}.xml".format(
            os.environ['BUILD_NUMBER']))
        local('mkdir -p {} && pytest -c ./config/deploy/pytest.cfg {} --cov-config=./config/deploy/pytest.cfg --junitxml={} --cov-report html:{}'.format(report_dir, "--boxed" if boxed else "",
                                                                                                                 output_path, report_dir))

def run_rolling_release_version():
    with lcd(os.path.join(proj_dir)):
        __showMessge(green, "working on {} ...".format(os.getcwd()))
        local('python  my_to_do\\build\\release_version_updater.py')


###
#
# gunicron web sever
#
###
__gunicorn_service = "python ./config/gunicorn/service.py"


def __localenv(cmd):
    __showMessge(green, "working on {} ...".format(os.getcwd()))
    local(cmd)


def start_gunicorn():
    with lcd(proj_dir):
        __localenv('{} --start '.format(__gunicorn_service))


def stop_gunicorn():
    with lcd(proj_dir):
        __localenv('{} --stop '.format(__gunicorn_service))


def restart_gunicorn():
    with lcd(proj_dir):
        __localenv('{} --restart '.format(__gunicorn_service))


def reload_gunicorn():
    with lcd(proj_dir):
        __localenv('{} --reload '.format(__gunicorn_service))

# to-do:
# after build, deploy to dev server first
# after build, deploy to prod server

# for dev :
# docker build
# docker run


if __name__ == "__main__":
    import sys
    sys.argv = ['fab', '-f', __file__, ] + sys.argv[1:]
    main()
