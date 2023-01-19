
def forigate_test():
    from tools import json2dict, dict2json
    out_path = "output.json"

    # 查看飞塔防火墙策略
    aa = json2dict(out_path)
    ff = aa["CONFIG"]["config firewall policy"]
    for i in ff:
        for _, attr in i.items():
            print(_)
            print(attr)
            # print("srcintf: %s" % attr[2][13:-1])
            # print("dstintf: %s" % attr[3][13:-1])
            print()

    # 查看飞塔防火墙用户和创建时间
    aa = json2dict(out_path)
    ff = aa["CONFIG"]["config user local"]
    for i in ff:
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
    from tools import append_excel
    name = "1.xlsx"
    wb = append_excel(name)
    ws = wb.worksheets[0]
    ws.append(["1", "2", "3"])
    wb.save(name)


if __name__ == "__main__":
    excel_test()
