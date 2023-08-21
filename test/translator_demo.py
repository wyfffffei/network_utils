#!/usr/local/bin/python3
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-2]
sys.path.append(os.sep.join(SCRIPT_DIR))

from network_utils.translator import Baidu_Translator
from network_utils.tools import dict2json

appid = ""
secretKey = ""

bt = Baidu_Translator(appid, secretKey)
res = bt.translate("banana")
print(res)

res = bt.translate_file("words.txt", is_save=True)
with open("output.txt", "w", encoding="utf-8") as f:
    if res is None:
        sys.exit(-1)
    f.writelines([w + "\n" for w in res])

