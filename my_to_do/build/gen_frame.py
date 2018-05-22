'''
Created on Sep 14, 2017

@author: mtk06979
'''
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import re


def postbuild(**kwds):
    pass


def __generateTemplate(server, src, dest):
    with open(server, 'r')as n, open(src, 'r') as c, open(dest, 'w') as cg:
        temp = n.read()

        tempcr = c.read()
        cli_content = re.search(r"\<\!\-\- client side area begin \-\-\>(?P<content>.*)\<\!\-\- client side area end \-\-\>",
                                tempcr,  re.S).group("content")

        cli_content = r"<!-- client side area begin -->{}<!-- client side area end -->".format(
            cli_content)
        print(cli_content)

        temp_cli = re.sub(
            r"\<\!\-\- client side area begin \-\-\>(?P<content>.*)\<\!\-\- client side area end \-\-\>",
            cli_content, temp,
            flags=re.S)

        if os.getenv("NODE_ENV", "development") == "development":
            temp_cli = re.sub(
                r"{%.*block.*%}\s*{%.*endblock.*%}", "", temp_cli, flags=re.S)
        else:
            print("skip django template removal in production")

        cg.write(temp_cli)
        print('gen done!!!')


def prebuild(**kwds):
    proj_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys_root = os.path.dirname(proj_path)

    nav_templates = os.path.join(
        sys_root, 'frontend', 'main_sys', 'templates', "index.html")

    cwd = os.getcwd()

    src = ""
    dest = ""
    if "cr_review_sys" in cwd:
        src = os.path.join(sys_root, "frontend",
                           "cr_review_sys", "templates", "index.html")
        dest = os.path.join(sys_root, "frontend",
                            "cr_review_sys", "templates", "index_gen.html")
    elif "md_analysis" in cwd:
        src = os.path.join(sys_root, 'frontend',
                           'md_analysis', 'templates', "index.html")
        dest = os.path.join(sys_root, 'frontend',
                            'md_analysis', 'templates', "index_gen.html")
    elif "main_sys" in cwd:
        src = os.path.join(sys_root, 'frontend',
                           'main_sys', 'templates', "home.html")
        dest = os.path.join(sys_root, 'frontend',
                            'main_sys', 'templates', "home_gen.html")
        __generateTemplate(nav_templates, src, dest)
        
        src = os.path.join(sys_root, 'frontend',
                           'main_sys', 'templates', "login.html")
        dest = os.path.join(sys_root, 'frontend',
                            'main_sys', 'templates', "login_gen.html")
        
    else:
        raise Exception("Incorrect working directory!")

    __generateTemplate(nav_templates, src, dest)



if __name__ == '__main__':

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("state", action="store",
                        help="specify the build state")

    args = parser.parse_args()

    argsDict = args.__dict__

    if argsDict['state'] == 'postbuild':
        postbuild(**argsDict)
    elif argsDict['state'] == 'prebuild':
        prebuild(**argsDict)
    else:
        print("unsupported actions")
