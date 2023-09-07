#!/usr/local/bin/python3

import os
import subprocess
import json
import argparse
import time


# GLOBAL VAR: ( 必须完善 )
# <WAF-Name>: [<Resource-Group>, <Subscription-Name>]
WAF_LIST = {
    "gw01": ["network-rg01", "sub-01"],
    "gw02": ["network-rg01", "sub-02"]
}
# [<WAF-POLICY-Resource-Group>, <WAF-POLICY-Subscription-Name>]
WAF_POLICY_CONF = ["network-rg", "network-sub"]

# Usage:
# python3 az-list-waf-conf.py -w <waf-name> -u


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())


def az_list_listener(CONF_PATH):
    if os.path.exists(CONF_PATH) and os.listdir(CONF_PATH):
        print("Config directory is not empty.")
    if not os.path.exists(CONF_PATH):
        os.mkdir(CONF_PATH)

    global WAF_LIST, WAF_POLICY_CONF
    for name, waf in WAF_LIST.items():
        cmd = "az network application-gateway show -n \"{}\" -g \"{}\" --subscription \"{}\" > \"{}/{}.json\"".format(name, waf[0], waf[1], CONF_PATH, name)
        subprocess.run(cmd, shell=True, check=True)
    cmd = "az network application-gateway waf-policy list -g \"{}\" --subscription \"{}\" > \"{}/waf_policy.json\"".format(WAF_POLICY_CONF[0], WAF_POLICY_CONF[1], CONF_PATH)
    subprocess.run(cmd, shell=True, check=True)


def parse_listener(listener):
    name = listener["name"]                                                                             # 侦听器 名称
    hostname = listener["hostName"] if listener.get("hostName") else '\n'.join(listener["hostNames"])   # 侦听器 主机名/域名
    protocol = listener["protocol"]                                                                     # 侦听器 协议
    port = listener["frontendPort"]["id"].split("/")[-1].split("_")[-1]                                 # 侦听器 端口
    cert = listener["sslCertificate"]["id"].split("/")[-1] if listener.get("sslCertificate") else ""    # 侦听器 证书
    cert_type = ""
    return [name, hostname, protocol, port, cert, cert_type]


def parse_redirection(redirections):
    P_REDIRECTION = dict()
    for redirection in redirections:
        red_name = redirection.get("name")                                                              # 重定向 名称
        target_listener = redirection.get("targetListener")                                             # 重定向 侦听器
        if not red_name or not target_listener:
            continue
        if P_REDIRECTION.get(red_name):
            print("ERROR REDIRECTION!")
            continue
        target_listener = target_listener["id"].split("/")[-1]
        P_REDIRECTION.update({red_name: target_listener})
    return P_REDIRECTION


def parse_rules(rules, redirections):
    P_RULES = dict()
    for rule in rules:
        lsn = rule["httpListener"]["id"].split("/")[-1]                                                                                         # 规则关联 侦听器
        name = rule["name"]                                                                                                                     # 规则 名称
        priority = rule["priority"] if rule.get("priority") else ""                                                                             # 规则 优先级
        backendAddressPool = rule["backendAddressPool"]["id"].split("/")[-1] if rule.get("backendAddressPool") else ""                          # 规则关联 后端池
        backendHttpSettings = rule["backendHttpSettings"]["id"].split("/")[-1] if rule.get("backendHttpSettings") else ""                       # 规则关联 后端设置
        redirect = redirections.get(rule["redirectConfiguration"]["id"].split("/")[-1]) if rule.get("redirectConfiguration") else ""             # 规则关联 重定向
        P_RULES.update({lsn: [name, priority, backendAddressPool, backendHttpSettings, redirect, ""]})
    return P_RULES


def parse_backendAddressPools(pools):
    P_POOLS = dict()
    for pool in pools:
        name = pool["name"]                                                                                                                     # 后端池 名称
        backendAddresses = '\n'.join(['\n'.join(bend.values()) for bend in pool["backendAddresses"]]) if pool.get("backendAddresses") else ""   # 后端池 IP
        P_POOLS.update({name: backendAddresses})
    return P_POOLS


def parse_backendHttpSettings(backendHttpSettings):
    P_backendHttpSettings = dict()
    for baends in backendHttpSettings:
        name = baends["name"]                                                               # 后端检测 名称
        protocol = baends["protocol"]                                                       # 后端检测 协议
        port = baends["port"]                                                               # 后端检测 端口
        hostname = baends["hostName"] if baends.get("hostName") else ""                     # 后端检测 替换主机名
        probe = baends["probe"]["id"].split("/")[-1] if baends.get("probe") else ""         # 后端检测 自定义探针
        P_backendHttpSettings.update({name: [protocol, port, hostname, probe]})
    return P_backendHttpSettings


def parse_waf_policy(policys):
    P_POLICYS = dict()
    for policy in policys:
        if not policy.get("httpListeners"):
            continue
        name = policy["name"]                                                               # WAF 策略名
        mode = policy["policySettings"]["mode"]                                             # WAF 保护模式
        state = policy["policySettings"]["state"]                                           # WAF 启用状态
        listeners = [lsn["id"].split("/")[-3] + '/' + lsn["id"].split("/")[-1] for lsn in policy["httpListeners"]]           # WAF 关联侦听器
        # print(listeners)
        for listener in listeners:
            if P_POLICYS.get(listener):
                print("ERROR WAF POLICY!")
                continue
            P_POLICYS.update({listener: [name, mode, state]})
    return P_POLICYS


def output2excel(WAF, POLICY, in_path, out_path):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["侦听器名称", "主机名/域名", "协议", "端口", "证书名称", "证书类型", "规则名称", "优先级", "后端池-后端目标", "后端池-后端设置", "重定向-侦听器", "重定向-外部站点", "后端池", "后端目标", "后端设置名称", "后端协议", "后端端口", "主机名", "自定义探针", "WAF策略-订阅", "WAF策略-资源组", "WAF策略-位置", "策略名", "保护模式", "启用状态"])

    GW = json2dict("{}/{}.json".format(in_path, WAF))
    WAF_P = json2dict("{}/{}.json".format(in_path, POLICY))

    # PARSE STEP
    redirections = GW["redirectConfigurations"]
    p_redirections = parse_redirection(redirections)

    rules = GW["requestRoutingRules"]
    p_rules = parse_rules(rules, p_redirections)

    backends = GW["backendAddressPools"]
    p_backends = parse_backendAddressPools(backends)

    backendsettings = GW["backendHttpSettingsCollection"]
    p_backendsettings = parse_backendHttpSettings(backendsettings)

    p_policys = parse_waf_policy(WAF_P)

    # READ LISTENER
    listeners = GW["httpListeners"]
    for listener in listeners:
	    # header = [GW, ""]
        lsn = parse_listener(listener)

        lsn_name = lsn[0]
        rule = p_rules[lsn_name] if p_rules.get(lsn_name) else ["", "", "", "", "", ""]

        backend_name = rule[2]
        backend = [backend_name, p_backends.get(backend_name) if p_backends.get(backend_name) else ""]

        backendsetting_name = rule[3] if rule[3] else ""
        backendsetting = [backendsetting_name] + p_backendsettings.get(backendsetting_name) if p_backendsettings.get(backendsetting_name) else ["", "", "", "", ""]

        policy = ["bsh-cloud-connectivity-n3", "platform-cnn3-p-corehub-rg01", "CN3"] + p_policys.get(arg.waf + '/' + lsn_name) if p_policys.get(arg.waf + '/' + lsn_name) else ["", "", "", "", "", ""]

        ws.append(lsn + rule + backend + backendsetting + policy)
        # ws.append(header + lsn + rule + backend + backendsetting + policy)

    wb.save(out_path)


if __name__ == "__main__":

    # GLOBAL VAR
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--waf", type=str, required=True, help="WAF Name Required")
    parser.add_argument("-p", "--policy", type=str, required=False, default="waf_policy", help="WAF Policy File Name")
    parser.add_argument("-u", "--update", action="store_true", required=False, help="run script to update all the config")
    arg = parser.parse_args()

    CONF_PATH = time.strftime("waf-conf-%y%m%d", time.localtime())
    if arg.update:
        az_list_listener(CONF_PATH)

    # WAF和策略文件名称
    # WAF = "gw01"
    # POLICY = "waf_policy"
    # output2excel(WAF, POLICY, in_path=CONF_PATH, out_path="P-"+ WAF + ".xlsx")

    output2excel(arg.waf, arg.policy, in_path=CONF_PATH, out_path="P-"+ arg.waf + ".xlsx")


