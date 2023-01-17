import os
import json


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())


def dict2json(dict, output_path, encoding="utf-8"):
    with open(output_path, "w", encoding=encoding) as f:
        f.write(json.dumps(dict, indent=4, separators=(',', ':')))


if __name__ == "__main__":
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
    # aa = json2dict(out_path)
    # ff = aa["CONFIG"]["config user local"]
    # for i in ff:
    #     for user, password in i.items():
    #         print("%-20s" % user[6:-1], end="")
    #         flag = 0
    #         for x in password:
    #             if "set passwd-time" in x:
    #                 print("%-20s" % x[16:])
    #                 flag = 1
    #         if not flag:
    #             print()
