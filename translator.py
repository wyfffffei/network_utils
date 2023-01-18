import http.client
import hashlib
import urllib
import random
import json
import time


class Baidu_Translator:
    # 百度翻译 API 调用
    def __init__(self, appid, secretKey, api="api.fanyi.baidu.com", url="/api/trans/vip/translate"):
        self.appid = appid
        self.secretKey = secretKey
        self.api = api
        self.url = url
        self.salt = random.randint(32768, 65536)

    def translate(self, q, fromLang="auto", toLang="zh") -> dict:
        time.sleep(1)
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


if __name__ == "__main__":
    # read the key
    with open("doc/bt_app_sec.txt", "r", encoding="utf-8") as f:
        appid, secretKey = f.readlines()[0].strip().split(",")
    
    bt = Baidu_Translator(appid, secretKey)
    res = bt.translate("banana")
    print(res)
