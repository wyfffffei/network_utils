#!/usr/local/bin/python3

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-2]
sys.path.append(os.sep.join(SCRIPT_DIR))

from network_utils import Connection

ip = input("IP_ADDRESS: ")
username = input("username: ")
# 逐行读取在远程执行的命令
command_file = "doc/centos_nginx"


try:
    from getpass import getpass
    password = getpass("password: ")
except ImportError:
    print("getpass is not installed.")
    password = input("password: ")

client = Connection(ip, username=username, password=password)

# 捕获额外需要输入的提示，返回对应的输入
confirm_flag = {
    "'s password:": "centos",
    "Enter expert password:": "centos",
    "Are you sure you want to continue?(Y/N)[N]": "y"
    }
# 实时返回远程输出信息
for stdout in client.send_command_file(command_file, confirm_flag=confirm_flag):
    print(stdout, end="")
client.close()


