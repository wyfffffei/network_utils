#!/usr/local/bin/python3
import os
import re
import json
import time
import ipaddress


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())


def subnet_caculator(ip):
    # 计算 IP 地址段包含范围
    if " " in ip:
        ip = re.sub(" ", "/", ip)
    try:
        net = ipaddress.ip_interface(ip).network
        if str(net.netmask) == "255.255.255.255":
            return str(net)[:-3]
        if str(net.netmask) == "255.255.255.254":
            return str(net[0]) + '-' + str(net[-1])
        return str(net[1]) + '-' + str(net[-2])
    except Exception as e:
        return ""


def search_hostname(config):
    # 查找 hostname
    _config_global = config["CONFIG"]["config system global"]

    host_pat = r"hostname\s\"\S+\""
    hostname = re.search(host_pat, ''.join(_config_global))
    return hostname.group().split("\"")[-2] if hostname else None


def search_interface(config):
    # 查找 接口信息
    _interface_all = config["CONFIG"]["config system interface"]

    for intf in _interface_all:
        intf_name = ''.join(list(intf.keys())[0]).split(" ")[-1].strip("\"")        # 接口名称
        intf = ' '.join(list(intf.values())[0])                                     # 接口配置原始信息
        
        ip_pat = r"\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+"                          # 正则匹配IP地址段
        root_int_pat = r"set\sinterface\s\"\S+\""                                   # 正则匹配父接口
        alias_pat = r"set\salias\s\"\S+\""                                          # 正则匹配接口别名

        if re.search(ip_pat, intf):
            if re.search(root_int_pat, intf):
                root_int = re.search(root_int_pat, intf).group().split(" ")[-1].strip("\"")
            else:
                root_int = intf_name
                intf_name = ""
            intf_alias = re.search(alias_pat, intf).group().split(" ")[-1].strip("\"") if re.search(alias_pat, intf) else ""
            ip_net = re.search(ip_pat, intf).group()
            # return ->（接口、子接口、接口别名、地址段、地址段范围）
            yield (root_int, intf_name, intf_alias, ip_net, subnet_caculator(ip_net))


def search_ft_object(config):
    # 查找 配置对象
    pass


def search_ipsecvpn(config):
    # 查找 ipsec vpn 兴趣流
    _phase1_config = config["CONFIG"]["config vpn ipsec phase1-interface"]
    _phase2_config = config["CONFIG"]["config vpn ipsec phase2-interface"]

    phase1 = dict()
    for item in _phase1_config:
        ph1_name = list(item.keys())[0].split(" ")[-1].strip("\"")
        ph1_item = ' '.join(list(item.values())[0])
        ph1_int_pat = r"set\sinterface\s\"\S+\""                    # 匹配VPN接口
        ph1_remote_pat = r"set\sremote-gw\s\d+.\d+.\d+.\d+"         # 匹配对端地址

        ph1_int = re.search(ph1_int_pat, ph1_item).group()[14:].strip("\"") if re.search(ph1_int_pat, ph1_item) else ""
        ph1_remote = re.search(ph1_remote_pat, ph1_item).group()[14:] if re.search(ph1_remote_pat, ph1_item) else ""
        # return --> (VPN接口、对端IP)
        if not phase1.get(ph1_name):
            phase1[ph1_name] = (ph1_int, ph1_remote)

    phase2 = dict()
    phase2_pat = r"set\sphase1name\s\"\S+\""                                                    # 匹配感兴趣流名称
    src_name_pat = r"set\ssrc-name\s\"\S+\""                                                    # 匹配感兴趣流源地址
    dst_name_pat = r"set\sdst-name\s\"\S+\""                                                    # 匹配感兴趣流目标地址
    src_subnet_pat = r"set\ssrc-subnet\s\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+"                 # 匹配感兴趣流源地址
    dst_subnet_pat = r"set\sdst-subnet\s\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+"                 # 匹配感兴趣流目标地址

    for item in _phase2_config:
        ph2_item = list(item.keys())[0].split(" ")[-1].strip("\"")
        ph2_detail = ' '.join(list(item.values())[0])
        ph2_name = re.search(phase2_pat, ph2_detail)
        if not ph2_name:
            continue
        ph2_name = ph2_name.group().split(" ")[-1].strip("\"")

        # 从 src-name 和 src-subnet 中选出非空元素
        src = {re.search(src_name_pat, ph2_detail), re.search(src_subnet_pat, ph2_detail)} ^ {None,}
        src_interest = ' '.join(src.pop().group().split(" ")[2:]).strip("\"") if src else ""
        dst = {re.search(dst_name_pat, ph2_detail), re.search(dst_subnet_pat, ph2_detail)} ^ {None,}
        dst_interest = ' '.join(dst.pop().group().split(" ")[2:]).strip("\"") if dst else ""

        # return --> (兴趣流源地址、兴趣流源范围、兴趣流目标地址、兴趣流目标范围)
        if not phase2.get(ph2_name):
            phase2[ph2_name] = {ph2_item: (src_interest, subnet_caculator(src_interest), dst_interest, subnet_caculator(dst_interest))}
            continue
        phase2[ph2_name].update({ph2_item: (src_interest, subnet_caculator(src_interest), dst_interest, subnet_caculator(dst_interest))})
    return (phase1, phase2)


def search_static_route(config):
    # 查找 静态路由
    _static_route = config["CONFIG"]["config router static"]

    dst_pat = r"set\sdst\s\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+"   # 匹配目标段
    gateway_pat = r"set\sgateway\s\d+\.\d+\.\d+\.\d+"               # 匹配网关
    interface_pat = r"set\sdevice\s\"\S+\""                         # 匹配接口
    comment_pat = r"set\scomment\s\"\S+\""                          # 匹配备注
    priority_pat = r"set\spriority\s\d+"                            # 匹配优先级
    status_pat = r"set\sstatus\s\S+"                                # 匹配状态

    for route in _static_route:
        route_id = list(route.keys())[0][5:]                        # edit "<route_id>"
        route_item = ' '.join(list(route.values())[0])              # route source config

        dst = re.search(dst_pat, route_item).group()[8:] if re.search(dst_pat, route_item) else "0.0.0.0 0.0.0.0"
        gateway = re.search(gateway_pat, route_item).group()[12:] if re.search(gateway_pat, route_item) else ""
        interface = re.search(interface_pat, route_item).group()[11:].strip("\"") if re.search(interface_pat, route_item) else ""
        comment = re.search(comment_pat, route_item).group()[12:].strip("\"") if re.search(comment_pat, route_item) else ""
        priority = re.search(priority_pat, route_item).group()[13:] if re.search(priority_pat, route_item) else ""
        status = re.search(status_pat, route_item).group()[11:] if re.search(status_pat, route_item) else ""
        # return -> (路由ID、目标段、目标段范围、网关、接口、备注、优先级、状态)
        yield (route_id, dst, subnet_caculator(dst), gateway, interface, comment, priority, status)


def output_2_excel(ft_policy):
    from openpyxl import Workbook
    wb = Workbook()

    # 创建表1（接口表）==> ["接口", "子接口", "接口别名", "地址段", "地址段范围"]
    ws_interface = wb.active
    ws_interface.title = "接口表"
    ws_interface.append(["接口", "子接口", "接口别名", "地址段", "地址段范围"])
    for intf in search_interface(ft_policy):
        ws_interface.append(intf)

    # 创建表2（IPSEC VPN表）==> ["IPSEC VPN名称", "VPN接口", "对端IP", "兴趣流名称", "兴趣流源地址", "兴趣流源范围", "兴趣流目标地址", "兴趣流目标范围"]
    ws_ipsec = wb.create_sheet("IPSEC VPN表")
    ws_ipsec.append(["IPSEC VPN名称", "VPN接口", "对端IP", "兴趣流名称", "兴趣流源地址", "兴趣流源范围", "兴趣流目标地址", "兴趣流目标范围"])
    ph1, ph2 = search_ipsecvpn(ft_policy)
    for ph_name, ph_item in ph1.items():
        for id_ph, (interest, stream_interest) in enumerate(ph2[ph_name].items()):
            if id_ph == 0:
                ws_ipsec.append((ph_name,) + ph_item + (interest,) + stream_interest)
                continue
            ws_ipsec.append(("", "", "", interest) + stream_interest)

    # 创建表3（路由表）==> ["路由ID", "目标段", "目标段范围", "网关", "接口", "备注", "优先级", "状态"]
    ws_route = wb.create_sheet("路由表")
    ws_route.append(["路由ID", "目标段", "目标段范围", "网关", "接口", "备注", "优先级", "状态"])
    for line in search_static_route(ft_policy):
        ws_route.append(line)
    
    # 输出文件名格式：<hostname>-<timestamp>.xlsx
    wb.save(search_hostname(ft_policy) + time.strftime("-%Y%m%d", time.localtime()) + ".xlsx")


def main():
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.sep.join(current_dir.split(os.sep)[:-1]))

    from conf_parser import FortiGate

    # GLOBAL: 配置源文件路径
    # path = "conf/Rexel_Wuhan_6-4_2092_202307251225.conf"

    if not sys.argv[1]:
        print("请添加参数: fortigate配置文件路径")
        sys.exit(-1)
    path = sys.argv[1]
    ft_policy = FortiGate(path).parse_policy()

    output_2_excel(ft_policy)


if __name__ == "__main__":
    main()
