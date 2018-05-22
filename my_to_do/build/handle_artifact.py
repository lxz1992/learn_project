'''
Created on Dec 13, 2017

@author: MTK06979
'''
import os
import glob
import shutil

if __name__ == '__main__':
    projRoot = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))
    cwd = os.getcwd()
    if "cr_review_sys" in cwd:
        distDir = os.path.join(projRoot, "cr_review_sys", "frontend", "dist")

    elif "md_analysis" in cwd:
        distDir = os.path.join(projRoot, "md_analysis", "frontend", "dist")
    else:
        raise Exception("not in correct working directory!")

    if os.path.exists(distDir):
        mapDir = os.path.join(projRoot, "md_analysis", "frontend", "map")
        if os.path.exists(mapDir):
            shutil.rmtree(mapDir)
        os.makedirs(mapDir)

        distDir = os.path.join(distDir, "**/*.js.map")
        print("checking existence: {}".format(distDir))
        for f in glob.glob(distDir):
            print(f)
            targetF = os.path.join(mapDir, os.path.basename(f))
            shutil.move(f, targetF)
