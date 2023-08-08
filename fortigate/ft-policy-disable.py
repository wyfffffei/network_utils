#!/usr/local/bin/python3
import re
import json
import pandas as pd


# 列出飞塔防火墙策略中的禁用策略
path = "conf/HQ-FW-20230718-parsed.json"
with open(path, 'r') as f:
    data = json.loads(f.read())
policy = data["CONFIG"]["config firewall policy"]

output = []
for item in policy:
    policy_name_pat = r"set\sname\s\"\S+\""
    p_detail = ' '.join(list(item.values())[0])
    if "set status disable" in p_detail:
        if re.search(policy_name_pat, p_detail):
            output.append(re.search(policy_name_pat, p_detail).group()[9:].strip("\"")) 

del data
df = pd.read_csv("conf/policy_standard_list_2023_07_18.csv")
# df = pd.read_excel("conf/policy_standard_list_2023_06_25.xlsx")
for index, row in df.iterrows():
    if row["名称"] in output:
        df.loc[index, "状态"] = "已禁用"
df.to_excel("output.xlsx")



