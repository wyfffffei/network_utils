import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from network_utils.conf_parser import *
from network_utils.tools import dict2json, json2dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, required=True, help="path of config file / commands needed to run on the remote")
    parser.add_argument("-d", "--device", type=str, help="ft or cp")
    parser.add_argument("-c", "--connection", action="store_true")
    parser.add_argument("-i", "--ip", type=str, help="remote ip address")
    parser.add_argument("-u", "--username", type=str, help="remote username")
    parser.add_argument("--port", type=int, default=22, help="remote port")
    arg = parser.parse_args()

    if arg.device:
        if arg.device not in {"ft", "cp"}:
            print("Invalid device given.")
            sys.exit(-1)

        output_path = arg.path.split(os.sep)[-1] + "_parsed.json"
        if arg.device == "ft":
            dict2json(FortiGate(arg.path).parse_policy(), output_path)
        elif arg.device == "cp":
            dict2json(CheckPoint(arg.path).parse_configuration(), output_path)
        print("save -> {}_parsed.json".format(arg.path))

    elif arg.connection:
        if not arg.ip or not arg.username:
            print("Username or password not found.")
            sys.exit(-1)
        
        from network_utils.connection import Connection
        try:
            from getpass import getpass
            password = getpass("Password: ")
        except ImportError:
            print("Use `pip install getpass` to install the getpass requirement.")
            sys.exit(-1)

        client = Connection(ip=arg.ip, username=arg.username, password=password, port=arg.port)
        confirm_flag = {
            "'s password:": "centos",
            "Enter expert password:": "centos",
            "Are you sure you want to continue?(Y/N)[N]": "y"
        }
        for stdout in client.send_command_file(arg.path, confirm_flag=confirm_flag):
            print(stdout)
        client.close()
