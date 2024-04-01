#!/usr/bin/python3
import os
import json
import time
import subprocess

import pandas as pd
from ipaddress import ip_network
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
            if sub.get("name"):
                subnet_name += (sub["name"] + '\n')
            else:
                subnet_name += ('-\n')
            if sub.get("addressPrefix"):
                subnet_addr += (sub["addressPrefix"] + '\n')
            else:
                subnet_addr += ('-\n')
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


def caculate_idle_subnet(all_network: list, used_network: list):
    # Func: 根据整体网段(all_network)和已用网段(used_network),输出空闲排序网段

    try:
        all_network = [ip_network(ip) for ip in all_network]
        used_network = [ip_network(ip) for ip in used_network]
    except Exception as e:
        print(e)
        return None

    network_last = []
    # 计算空闲子网
    for cidr in used_network:
        if not network_last:
            network_last = all_network
        temp = []
        for block in network_last:
            if cidr.subnet_of(block):
                temp += list(block.address_exclude(cidr))
                continue
            temp += [block]
        network_last = temp

    return sorted(network_last)


def change2IPV4(ip_addr):
    # 选一个地址段做归一化处理
    if len(ip_addr.split("\n")) > 1:
        return ip_network(ip_addr.split("\n")[0])
    return ip_network(ip_addr)


def output2excel(output, conf_path="conf", network_all=""):
    # PARAM:
    # output:    输出文件名
    # conf_path: 配置文件路径

    _TITLE = "Azure CN Vnet 资源列表"
    COLUMNS = ["订阅", "资源组", "虚拟网络名称", "类型", "位置", "地址空间", "子网名称", "子网地址空间", "对等名称", "对等互联状态", "对端路径", "对端地址空间"]

    ls = os.listdir(conf_path)
    DF = pd.DataFrame(columns=COLUMNS)

    # 写入
    index = 0
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
            DF.loc[index] = ((sub[:-5],) + a + b + c)
            index += 1

    # 地址归一化
    DF["地址空间-bak"] = DF["地址空间"]
    DF["地址空间-bak"] = DF["地址空间-bak"].apply(change2IPV4)

    # 计算空闲子网
    if network_all:
        network_2_exclude = list(DF["地址空间-bak"])
        ret = caculate_idle_subnet(network_all, network_2_exclude)

        # 插入空闲网段行
        if ret:
            start = len(DF.index)
            for cid, cidr in enumerate(ret):
                print()
                DF.loc[start + cid] = list(5*'-') + [str(cidr)] + list(6*'-') + [cidr]
        else:
            print("Idle Subnet Caculating Error.")

    # 排序
    sorted_df = DF.sort_values(by="地址空间-bak")
    sorted_df = sorted_df.drop("地址空间-bak", axis=1)

    # 输出
    sorted_df.to_excel(output + ".xlsx", index=False)


if __name__ == "__main__":
    # 生成配置文件名
    CONF_PATH = time.strftime("vnet-conf-%y%m%d", time.localtime())

    # 根据该网段,生成vnet未使用到的网段(可不加)
    NETWORK_ALL = ["10.20.0.0/16"]

    if os.path.exists(CONF_PATH) and os.listdir(CONF_PATH):
        print("Config directory is not empty.")

    # 拉取vnet配置
    for account in tqdm(get_az_account()):
        get_az_vnet(account, CONF_PATH)

    output2excel("VNET-brief" + time.strftime("-%y%m%d", time.localtime()), conf_path=CONF_PATH, network_all=NETWORK_ALL)

