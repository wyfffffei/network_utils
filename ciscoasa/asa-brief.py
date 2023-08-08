#/usr/local/bin/python3
import re
import time
import ipaddress

from openpyxl import Workbook
from ciscoconfparse import CiscoConfParse

# pip3 install ciscoconfparse
# https://github.com/mpenning/ciscoconfparse
# http://pennington.net/tutorial/ciscoconfparse/ccp_tutorial.html


def search_hostname(config):
    hostname = config.find_objects("^hostname")
    if not hostname:
        return None
    return hostname[0].text[9:]


def search_obj(config, obj_type, obj_name):
    objs = config.find_objects("^{} network {}$".format(obj_type, obj_name))
    resv = []
    for obj in objs:
        if obj_type == "object":
            for item in obj.children:
                item = item.text.split(" ")[2:]
                resv += item
        else:
            for item in obj.re_search_children(r"network-object"):
                item = item.text.split(" ")[2:]
                if item[0] == "host" or item[0] == "object":
                    item.pop(0)
                resv.append('/'.join(item))
    return resv


def search_interface(config):
    _RE_content_title = ["interface name", "nameif", "security-level", "ip address", "net mask", "vlan", "shutdown", "ACL group", "description"]

    acl_gs = config.find_objects("^access-group\s")
    AG = dict()
    for acl_g in acl_gs:
        acl_g = acl_g.text.split(" ")
        AG[acl_g[-1]] = acl_g[1]

    intf_obj = config.find_objects('^interface\s+')
    for obj in intf_obj:
        # 接口名
        intf_name = ' '.join(obj.text.split(" ")[1:])
        # nameif
        intf_nameif = obj.re_match_iter_typed(
            r'^\snameif\s(\S+)', result_type=str, group=1, default='')
        # 优先级
        intf_sec = obj.re_match_iter_typed(
            r'^\ssecurity-level\s(\d+)', result_type=str, group=1, default='')
        # IP地址
        ip_addr = obj.re_match_iter_typed(
            r'^\sip\saddress\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)', result_type=str, group=1, default='')
        # 子网掩码
        net_mask = obj.re_match_iter_typed(
            r'^\sip\saddress\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)', result_type=str, group=2, default='')
        # vlan号
        vlan = obj.re_match_iter_typed(
            r'^\svlan\s(\d+)', result_type=str, group=1, default='')
        # 开关状态
        shutdown = obj.re_match_iter_typed(
            r'^\s(shutdown)', result_type=str, group=1, default='')
        # 关联 ACL-Group
        acl_group = AG.get(intf_nameif) if AG.get(intf_nameif) else ""
        # 描述
        description = obj.re_match_iter_typed(
            r'^\sdescription\s(.*)', result_type=str, group=1, default='')
        yield [intf_name, intf_nameif, intf_sec, ip_addr, net_mask, vlan, shutdown, acl_group, description]


def search_route_table(config):
    _RE_content_title = ["IP", "Netmask", "Next hop"]

    route_obj = config.find_objects('^route')
    for obj in route_obj:
        route_table = re.findall(r'\d+.\d+.\d+.\d+', obj.text)
        if not isinstance(route_table, list):
            continue
        yield route_table


def main():
    # GLOBAL VAR
    path = "conf/lan-asa.txt"

    config = CiscoConfParse(path, syntax="asa")
    acl_rules = config.find_objects("^access-list")

    wb = Workbook()
    ws = wb.active
    ws.title = "Cisco ASA 防火墙 ACL 访问策略"
    ws.append(["源端口", "ACL类型", "动作", "协议", "源地址", "目标地址", "端口"])

    obj_dict = dict()
    for acl in acl_rules:
        acl = acl.text.split(" ")
        if acl[2] != "remark":
            prefix = acl[1:5]
            acl = acl[5:]
        else:
            ws.append(acl[:3] + [' '.join(acl[3:])])
            continue

        out = []
        skip = False
        addr_block = ""
        for eid, entry in enumerate(acl):
            if skip:
                skip = False
                continue
            if entry == "any":
                out.append(entry)
            elif entry == "host" or entry == "eq":
                out.append(acl[eid + 1])
                skip = True
            elif entry == "object" or entry == "object-group":
                obj = acl[eid + 1]
                if not obj_dict.get(obj):
                    obj_dict[obj] = search_obj(config, entry, obj)
                out.append(obj)
                skip = True
            elif entry == "log":
                continue
            else:
                # addr block
                if addr_block:
                    try:
                        addr_block += ('/' + str(ipaddress.ip_network(addr_block + "/" + entry).prefixlen))
                    except Exception as e:
                        addr_block += (" " + entry)
                    out.append(addr_block)
                    addr_block = ""
                else:
                    addr_block = entry

        ws.append(prefix + out)

    ws2 = wb.create_sheet(title="ACL Object Map")
    ws2.append(["对象(组)名", "映射IP/段"])
    for o_name, obj in obj_dict.items():
        ws2.append([o_name, '\n'.join(obj)])

    ws3 = wb.create_sheet(title="接口信息")
    ws3.append(["interface name", "nameif", "security-level", "ip address", "net mask", "vlan", "shutdown", "with group", "description"])
    for interface in search_interface(config):
        ws3.append(interface)

    ws4 = wb.create_sheet(title="路由表")
    ws4.append(["IP", "Netmask", "Next hop"])
    for route in search_route_table(config):
        ws4.append(route)

    hostname = search_hostname(config)
    wb.save(hostname + time.strftime("-%Y%m%d", time.localtime()) + ".xlsx")


if __name__ == "__main__":
    main()

