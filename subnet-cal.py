#!/usr/local/bin/python3
import sys
import ipaddress as ip

param = sys.argv[1:]
if not param:
    print("No parameter given.")
    sys.exit(-1)

for pa in param:
    try:
        net = ip.ip_interface(pa).network
        available_ip = len(list(net))
        net_broadcast = net.broadcast_address

        if str(net.netmask) == "255.255.255.255":
            available_ip = available_ip
            range_ip = (str(net).split("/")[-2], str(net).split("/")[-2])
            net_broadcast = ""

        elif str(net.netmask) == "255.255.255.254":
            available_ip = available_ip
            range_ip = (str(net[0]), str(net[-1]))
            net_broadcast = ""

        else:
            available_ip -= 2
            range_ip = (str(net[1]), str(net[-2]))

        print("可用ip: {}".format(available_ip))
        print("网络: {}, {}".format(net.compressed, net.with_netmask))
        print("范围: {}-{}".format(range_ip[0], range_ip[-1]))
        print("广播ip: {}".format(net_broadcast))
        print(20 * '-')

    except Exception as e:
        print(e)

