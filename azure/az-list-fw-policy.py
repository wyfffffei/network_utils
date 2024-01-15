#!/usr/local/bin/python3
import os
import json
import time
from openpyxl import Workbook

import argparse

# 列出 Azure 防火墙的策略（先将订阅、资源组、防火墙名称和防火墙策略填入）
# python3 az-list-fw.policy.py
# https://learn.microsoft.com/zh-cn/cli/azure/network/firewall/policy/rule-collection-group?view=azure-cli-latest#az-network-firewall-policy-rule-collection-group-list


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())

def list_fw_policy(subscription: str, resource_group: str, fw_name: str, policy_name: list):
    wb = Workbook()
    ws = wb.active
    ws.title = "FW网络策略"
    ws.append(["防火墙策略", "规则集合组", "集合组优先级", "规则集合", "行为", "规则优先级", "规则名称", "规则类型", "规则描述", "源IP", "源IP组", "目的IP", "目的IP组", "目的FQDN", "目的端口", "IP协议", "协议", "IPv6规则", "转换后IP", "转换后FQDN", "转换后端口", "FQDN", "FQDN标记", "请求插入头部", "目标URL", "terminateTls", "webCategories"])

    for p in policy_name:
        os.system("az network firewall policy rule-collection-group list -g {} --subscription {} --policy {} > {}.json".format(resource_group, subscription, p, p))

        policys = json2dict(p + ".json")
        for policy in policys:
            p_name = policy["name"]
            p_priority = policy["priority"]
            ruleCollections = policy["ruleCollections"]
            for rid, rules in enumerate(ruleCollections):
                rules_name = rules["name"]
                rules_action = rules["action"]["type"]
                rules_priority = rules["priority"]
        
                for rule in rules["rules"]:
                    r_name = rule["name"]
                    r_ruleType = rule["ruleType"]
                    r_description = rule["description"]
                    r_sourceAddresses = '\n'.join(rule["sourceAddresses"]) if rule.get("sourceAddresses") else "-"
                    r_sourceIpGroups = '\n'.join(rule["sourceIpGroups"]) if rule.get("sourceIpGroups") else "-"
                    r_destinationAddresses = '\n'.join(rule["destinationAddresses"]) if rule.get("destinationAddresses") else "-"
                    r_destinationIpGroups = '\n'.join(rule["destinationIpGroups"]) if rule.get("destinationIpGroups") else "-"
                    r_destinationFqdns = '\n'.join(rule["destinationFqdns"]) if rule.get("destinationFqdns") else "-"
                    r_destinationPorts = '\n'.join(rule["destinationPorts"]) if rule.get("destinationPorts") else "-"
                    r_ipProtocols = '\n'.join(rule["ipProtocols"]) if rule.get("ipProtocols") else "-"
                    r_protocols = str(rule["protocols"])[1:-1] if rule.get("protocols") else "-"
                    r_ipv6Rule = '\n'.join(rule["ipv6Rule"]) if rule.get("ipv6Rule") else "-"
                    r_translatedAddress = rule["translatedAddress"] if rule.get("translatedAddress") else "-"
                    r_translatedFqdn = '\n'.join(rule["translatedFqdn"]) if rule.get("translatedFqdn") else "-"
                    r_translatedPort = rule["translatedPort"] if rule.get("translatedPort") else "-"
                    r_fqdns = '\n'.join(rule["targetFqdns"]) if rule.get("targetFqdns") else "-"
                    r_fqdnTags = '\n'.join(rule["fqdnTags"]) if rule.get("fqdnTags") else "-"
                    r_httpHeadersToInsert = '\n'.join(rule["httpHeadersToInsert"]) if rule.get("httpHeadersToInsert") else "-"
                    r_targetFqdns = '\n'.join(rule["targetFqdns"]) if rule.get("targetFqdns") else "-"
                    r_targetUrls = '\n'.join(rule["targetUrls"]) if rule.get("targetUrls") else "-"
                    r_terminateTls = '\n'.join(rule["terminateTls"]) if rule.get("terminateTls") else "-"
                    r_webCategories = '\n'.join(rule["webCategories"]) if rule.get("webCategories") else "-"
        
                    ws.append([p, p_name, p_priority, rules_name, rules_action, rules_priority, r_name, r_ruleType, r_description, r_sourceAddresses, r_sourceIpGroups, r_destinationAddresses, r_destinationIpGroups, r_destinationFqdns, r_destinationPorts, r_ipProtocols, r_protocols, r_ipv6Rule, r_translatedAddress, r_translatedFqdn, r_translatedPort, r_fqdns, r_fqdnTags, r_httpHeadersToInsert, r_targetUrls, r_terminateTls, r_webCategories])

    wb.save(fw_name + time.strftime("-%Y%m%d", time.localtime()) + ".xlsx")


if __name__ == "__main__":
    # GLOBAL VAR
    subscription = ""
    resource_group = ""
    fw_name = ""
    policy_name = []

    parser = argparse.ArgumentParser(
        description=
        """
        Cheatsheet:
        python az-list-fw-policy.py -s <subscription> -r <resource-group> -f <fw-name> -p <policy-name-1> <policy-name-2>
        """
    )
    parser.add_argument("-s", "--subscription", type=str, help="firewall subscription")
    parser.add_argument("-r", "--resource_group", type=str, help="firewall resource group")
    parser.add_argument("-f", "--fw_name", type=str, help="firewall name")
    parser.add_argument("-p", "--policy_name", nargs='+', help="firewall policy name list")
    arg = parser.parse_args()
    
    subscription = arg.subscription if arg.subscription else subscription
    resource_group = arg.resource_group if arg.resource_group else resource_group
    fw_name = arg.fw_name if arg.fw_name else fw_name
    policy_name = arg.policy_name if arg.policy_name else policy_name

    list_fw_policy(subscription, resource_group, fw_name, policy_name)
    

