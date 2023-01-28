# Network Utils

网络工具包。

依赖（可选）：

```bash
pip install tqdm
```

执行：（**python3**）

```bash
python xxx.py
```



## conf_parser.py

解析配置文件到 `dict` 或者 `json` 格式，目前支持👇：

- 飞塔防火墙（图形界面 `backup` 文件）

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

- CheckPoint 网关（`save configuration`）

```python
# 主函数部分
if __name__ == "__main__":
    conf_path = "doc/gaia_os_cp_gw.txt"
    CP = CheckPoint(conf_path)
    conf = CP.parse_configuration()
    print(conf["set"]["installer"]["policy"])
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



## connection.py

`ssh` 远程连接脚本。

- 依赖（可选）

```bash
pip install getpass
```

- 直接调用

```python
# 主函数部分
if __name__ == "__main__":
    ip = input("IP_ADDRESS: ")
    username = input("username: ")
    
    try:
        from getpass import getpass
        password = getpass("password: ")
    except ImportError:
        print("getpass is not installed.")
        password = input("password: ")
    
    client = Connection(ip, username=username, password=password)
    # 逐行读取在远程执行的命令（参考示例：doc/centos_nginx）
    command_file = "doc/centos_nginx"
    
    # 捕获额外需要输入的提示，返回对应的输入
    confirm_flag = {
        "'s password:": "centos",
        "Enter expert password:": "centos",
        "Are you sure you want to continue?(Y/N)[N]": "y"
        }
    # 实时返回远程输出信息
    for stdout in client.send_command_file(command_file, confirm_flag=confirm_flag):
        print(stdout)
    client.close()
```



