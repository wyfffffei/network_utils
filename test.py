import os
import sys


def forigate_test(conf_path="doc/FortiGate01.conf", out_path="output/output.json"):
    from network_utils.tools import dict2json
    from network_utils.conf_parser import FortiGate
    # 配置文件位置 和 解析输出位置

    FT = FortiGate(conf_path)
    p = FT.parse_policy()
    # print(p)

    dict2json(p, out_path)

    # 查看飞塔防火墙策略
    # fp = p["CONFIG"]["config firewall policy"]
    # for i in fp:
    #     for _, attr in i.items():
    #         print(_)
    #         print(attr)
    #         # print("srcintf: %s" % attr[2][13:-1])
    #         # print("dstintf: %s" % attr[3][13:-1])
    #         print()

    # 查看飞塔防火墙用户和创建时间
    user_list = []
    fu = p["CONFIG"]["config user local"]
    for i in fu:
        for user, password in i.items():
            user_item = []
            # print("%-20s" % user[6:-1], end="")
            user_item.append(user[6:-1])
            for x in password:
                # if "set email-to" in x:
                #     # print("%-40s" % x[14:-1], end="")
                #     user_item.append(x[14:-1])
                if "set passwd-time" in x:
                    # print("%-20s" % x[16:], end="")
                    user_item.append(x[16:])
                if "set two-factor" in x:
                    user_item.append("enabled")
            if len(user_item) <= 2:
                user_item.insert(1, "")
            user_list.append(user_item)
    return user_list

def excel_test():
    from network_utils.tools import append_excel
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
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))

    # arg_test()
    # check_hostname()

    x = forigate_test(conf_path="doc/lgshareFortiGate01_20230301_1116.conf", out_path="output/ft_users.json")
    from network_utils.tools import append_excel
    name = "output/output_ft_users.xlsx"
    wb = append_excel(name)
    ws = wb.worksheets[0]
    # ws.append(["VPN用户名", "邮箱", "创建账户时间"])
    for i in x:
        ws.append(i)
    wb.save(name)

    