# Network Utils

网络工具包。

依赖（可选）：

```bash
pip install tqdm
```



## conf_parser.py

解析配置文件到 `dict` 或者 `json` 格式。

- 飞塔防火墙

```bash
# 主函数部分
if __name__ == "__main__":
    # 配置文件位置 和 解析输出位置
    conf_path = r"D:\workspace\network_utils\doc\cfgbackup_ft_fw01.conf"
    out_path = "output.json"

    FT = FortiGate(conf_path)
    p = FT.parse_policy()
    # print(p)

    from tools import dict2json
    dict2json(p, out_path)
```



## translator.py

翻译 `api` 调用器。

- 百度 API

```python
# 主函数部分
if __name__ == "__main__":
    # 从文件读取 appid 和 secretKey
    with open("doc/bt_app_sec.txt", "r", encoding="utf-8") as f:
        appid, secretKey = f.readlines()[0].strip().split(",")
    
    bt = Baidu_Translator(appid, secretKey)
    
    # 翻译单词
    res = bt.translate("banana")
    print(res)

    # 翻译文件（逐行翻译，逐行输出）
    res = bt.translate_file("doc/words.txt", is_save=True)
    with open("doc/output.txt", "w", encoding="utf-8") as f:
        f.writelines([w + "\n" for w in res])
```

