
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


if __name__ == "__main__":
    arg_test()
