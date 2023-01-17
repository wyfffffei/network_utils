# Network Utils

网络工具包。



## conf_parser.py

解析配置文件到 `dict` 或者 `json` 格式。

依赖（可选）：

```bash
pip install tqdm
```

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

