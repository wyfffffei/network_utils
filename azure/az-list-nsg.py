#!/usr/bin/python3
import os
import json
import time
import subprocess
import pandas as pd

import argparse


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())

def list_nsg_rule(subscription, resource_group, nsg_name, timestamp):
    cmd = "az network nsg show --subscription {} -g {} -n {} > {}{}.json".format(subscription, resource_group, nsg_name, nsg_name, timestamp)
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, encoding="utf-8")
    except Exception as e:
        print(e)

def parse_nsg_rule(nsg_config):
    try:
        NSG = json2dict(nsg_config)
    except Exception as e:
        print(e)
        return
    defaultSecurityRules= NSG.get("defaultSecurityRules") if NSG.get("defaultSecurityRules") else []
    securityRules = NSG.get("securityRules") if NSG.get("securityRules") else []
    return defaultSecurityRules + securityRules

def output2excel(rule_list, filename):
    all_keys = sorted(set().union(*[d.keys() for d in rule_list]))
    
    # 创建包含键的DataFrame（第一行）
    df = pd.DataFrame([all_keys], columns=all_keys)
    
    # 添加每个字典的值行
    for d in rule_list:
        row = {col: d.get(col, "") for col in all_keys}
        df = pd.concat([df, pd.DataFrame([row], columns=all_keys)])
    
    # 按优先级、出入方向排序
    # 取出第一行
    column_row = df.iloc[[0]]
    data = df.iloc[1:]

    # 剩下行按方向分组，按优先级排序
    grouded_data = data.groupby("direction")
    sorted_groups = pd.concat([group.sort_values("priority") for name, group in grouded_data])

    # 合并第一行，写入Excel文件
    result = pd.concat([column_row, sorted_groups])
    result.to_excel(filename, index=False, header=False)


if __name__ == "__main__":
    # GLOBAL VAR
    subscription = ""
    resource_group = ""
    nsg_name = ""

    parser = argparse.ArgumentParser(
        description=
        """
        Cheatsheet:
        python az-list-nsg.py -s <subscription> -r <resource-group> -n <nsg-name>
        """
    )
    parser.add_argument("-s", "--subscription", type=str, help="nsg subscription")
    parser.add_argument("-r", "--resource_group", type=str, help="nsg resource group")
    parser.add_argument("-n", "--nsg_name", type=str, help="nsg name")
    arg = parser.parse_args()
    
    subscription = arg.subscription if arg.subscription else subscription
    resource_group = arg.resource_group if arg.resource_group else resource_group
    nsg_name = arg.nsg_name if arg.nsg_name else nsg_name

    timestamp = time.strftime("-%y%m%d", time.localtime())
    list_nsg_rule(subscription, resource_group, nsg_name, timestamp)
    output2excel(parse_nsg_rule(nsg_name + timestamp + ".json"), nsg_name + timestamp + ".xlsx")

