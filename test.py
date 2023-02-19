
def forigate_test():
    from .tools import dict2json
    from .conf_parser import FortiGate
    # 配置文件位置 和 解析输出位置
    conf_path = "doc/FortiGate01.conf"
    out_path = "doc/output.json"

    FT = FortiGate(conf_path)
    p = FT.parse_policy()
    # print(p)

    dict2json(p, out_path)

    # 查看飞塔防火墙策略
    fp = p["CONFIG"]["config firewall policy"]
    for i in fp:
        for _, attr in i.items():
            print(_)
            print(attr)
            # print("srcintf: %s" % attr[2][13:-1])
            # print("dstintf: %s" % attr[3][13:-1])
            print()

    # 查看飞塔防火墙用户和创建时间
    fu = p["CONFIG"]["config user local"]
    for i in fu:
        for user, password in i.items():
            print("%-20s" % user[6:-1], end="")
            flag = 0
            for x in password:
                if "set passwd-time" in x:
                    print("%-20s" % x[16:])
                    flag = 1
            if not flag:
                print()


def excel_test():
    from .tools import append_excel
    name = "1.xlsx"
    wb = append_excel(name)
    ws = wb.worksheets[0]
    ws.append(["1", "2", "3"])
    wb.save(name)


def arg_test():
    import os
    print(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[-1])


def check_hostname():
    import re
    hostname = "[root@centos-7 /etc]#"
    linux_host = re.compile("^\[(\w|-)+@(\w|-)+ (\w|-|/|~)+\]#", re.IGNORECASE)
    if linux_host.match(hostname):
        print(linux_host.match(hostname)[0].split(" ")[0].split("@")[1])

    hostname = """WARNING: File System Check Recommended! An unsafe reboot may have caused an inconsistency in the disk drive.
It is strongly recommended that you check the file system consistency before proceeding.
Please run 'execute disk list' and then 'execute disk scan <ref#>'.
Note: The device will reboot and scan the disk during startup. This may take up to an hour.
FortiGate-VM64 #"""
    hostname = hostname.split("\n")[-1]
    device_host = re.compile("^(\w|-)+ \(?(\w|-)*\)? ?#", re.IGNORECASE)
    if device_host.match(hostname):
        print(device_host.match(hostname)[0].split(" ")[0])
    # print(all(allowed.match(x) for x in hostname.split(".")))


if __name__ == "__main__":
    # arg_test()
    check_hostname()
    