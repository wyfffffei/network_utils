#!/usr/local/bin/python3
import os
import json
import subprocess
import time
from tqdm import tqdm


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())


def parse_basic_info(config):
    if not config:
        return None

    # return -> (资源组, 虚拟网络名称, 类型, 位置, 地址空间)
    for item in config:
        res_group = item["resourceGroup"]
        vnet_name = item["name"]
        vnet_type = item["type"]
        location = item["location"]
        addrspace = '\n'.join(item["addressSpace"]["addressPrefixes"])
        yield (res_group, vnet_name, vnet_type, location, addrspace)


def parse_subnet(config):
    if not config:
        return None
    
    # return -> (子网名称, 子网地址空间)
    for item in config:
        subnet_name = ''
        subnet_addr = ''
        for sub in item["subnets"]:
            subnet_name += (sub["name"] + '\n')
            subnet_addr += (sub["addressPrefix"] + '\n')
        subnet_name = subnet_name.strip()
        subnet_addr = subnet_addr.strip()
        yield (subnet_name, subnet_addr)
    

def parse_peering(config):
    if not config:
        return None
    
    # return -> (对等名称, 对等互联状态, 对端路径, 对端地址空间)
    for item in config:
        peer_name = ''
        peer_state = ''
        peer_remoteVN = ''
        peer_remoteADDR = ''
        for peer in item["virtualNetworkPeerings"]:
            peer_name += (peer["name"] + '\n')
            peer_state += (peer["peeringState"] + '\n')
            peer_remoteVN += (peer["remoteVirtualNetwork"]["id"] + '\n')
            peer_remoteADDR += ('\n'.join(peer["remoteAddressSpace"]["addressPrefixes"]) + '\n')
        peer_name = peer_name.strip()
        peer_state = peer_state.strip()
        peer_remoteVN = peer_remoteVN.strip()
        peer_remoteADDR = peer_remoteADDR.strip()
        yield (peer_name, peer_state, peer_remoteVN, peer_remoteADDR)


def get_az_account():
    # FUNC: 列出 Azure 订阅名

    cmd = "az account list | jq '.[].name'"
    ret = subprocess.run(cmd, shell=True, check=True, capture_output=True, encoding="utf-8")

    for line in ret.stdout.split("\n"):
        if not line:
            continue
        yield line.strip("\"")


def get_az_vnet(account, output="conf"):
    # PARAM:
    # account: Azure 订阅名
    # output:  输出 Vnet 配置文件位置

    if not os.path.exists(output):
        os.mkdir(output)
    cmd = 'az network vnet list --subscription "{}" > "{}/{}.json"'.format(account, output, account)
    subprocess.run(cmd, shell=True, check=True, capture_output=True, encoding="utf-8")
    

def output2excel(output, conf_path="conf"):
    # PARAM:
    # output:    输出文件名
    # conf_path: 配置文件路径

    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["Azure CN Vnet 资源列表"])
    ws.append(["订阅", "资源组", "虚拟网络名称", "类型", "位置", "地址空间", "子网名称", "子网地址空间", "对等名称", "对等互联状态", "对端路径", "对端地址空间"])

    ls = os.listdir(conf_path)
    for sub in tqdm(ls):
        config = json2dict(conf_path + os.sep + sub)

        infos = []
        subnets = []
        peerings = []
        for info in parse_basic_info(config):
            infos.append(info)
        for subnet in parse_subnet(config):
            subnets.append(subnet)
        for peering in parse_peering(config):
            peerings.append(peering)

        for a, b, c in zip(infos, subnets, peerings):
            ws.append((sub[:-5],) + a + b + c)

    wb.save(output + ".xlsx")


if __name__ == "__main__":
    CONF_PATH = time.strftime("vnet-conf-%y%m%d", time.localtime())

    if os.path.exists(CONF_PATH) and os.listdir(CONF_PATH):
        print("Config directory is not empty.")

    for account in tqdm(get_az_account()):
        get_az_vnet(account, CONF_PATH)

    output2excel("VNET-brief" + time.strftime("-%y%m%d", time.localtime()), CONF_PATH)

