import http.client
import hashlib
import urllib
import random
import json
import time
import os
import sys
from tqdm import tqdm


class Baidu_Translator:
    # 百度翻译 API 调用
    def __init__(self, appid, secretKey, api="api.fanyi.baidu.com", url="/api/trans/vip/translate"):
        self.appid = appid
        self.secretKey = secretKey
        self.api = api
        self.url = url
        self.salt = random.randint(32768, 65536)

    def translate(self, q, fromLang="auto", toLang="zh") -> dict:
        sign = self.appid + q + str(self.salt) + self.secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        url = self.url + '?appid=' + self.appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        self.salt) + '&sign=' + sign

        try:
            httpClient = http.client.HTTPConnection(self.api)
            httpClient.request('GET', url)

            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            return result

        except Exception as e:
            print (e)

        finally:
            if httpClient:
                httpClient.close()

    def translate_file(self, path, fromLang="auto", toLang="zh", is_save=False) -> list:
        if not os.path.exists(path):
            print("File path is invalid.")
            return None
    
        with open(path, 'r', encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            words = set(lines)
        
        brain = {}
        for word in tqdm(words):
            time.sleep(1)
            ans = self.translate(word, fromLang=fromLang, toLang=toLang)
            brain[word] = ans["trans_result"][0]["dst"]
        
        if is_save:
            # save the dict translation with json
            from network_utils.tools import dict2json
            dict2json(brain, "translation_{}.json".format(time.strftime("%Y%m%d%H%M%S", time.localtime())))
        
        return [brain[line] for line in lines]


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))

    # read the key
    with open("doc/bt_app_sec.txt", "r", encoding="utf-8") as f:
        appid, secretKey = f.readlines()[0].strip().split(",")
    
    bt = Baidu_Translator(appid, secretKey)
    
    # 翻译单词
    # res = bt.translate("banana")
    # print(res)

    # 翻译文件（逐行翻译，逐行输出）
    res = bt.translate_file("doc/words.txt", is_save=True)
    with open("output/translate_result.txt", "w", encoding="utf-8") as f:
        f.writelines([w + "\n" for w in res])
