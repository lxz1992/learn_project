'''
Created on Nov 16, 2017

@author: MTK06979
'''
import json
import sys
import copy


if __name__ == '__main__':

    print(sys.argv)
    with open(sys.argv[1], "r", encoding='utf8') as f, open(sys.argv[2], "w", encoding='utf8') as fw:
        data = json.load(f)
#         output = copy.deepcopy(data)

        concern = filter(lambda x: x["status"] != "ABANDONED", data["commits"])
        data["commits"] = list(concern)

        for commit in data["commits"]:
            for patchset in commit["patchSets"]:
                if patchset["author"]["name"].lower() == "eric":
                    patchset["author"]["name"] = "Yang Deng"
                    patchset["author"]["email"] = "yang.deng@mediatek.com"
                    patchset["author"]["username"] = "mtk14591"
                    
                if patchset["uploader"]["name"].lower() == "eric":
                    patchset["uploader"]["name"] = "Yang Deng"
                    patchset["uploader"]["email"] = "yang.deng@mediatek.com"
                    patchset["uploader"]["username"] = "mtk14591"
                    
            print(commit["status"])

        json.dump(data, fw, ensure_ascii=False, indent=4)
