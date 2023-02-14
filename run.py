import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from network_utils.conf_parser import *
from network_utils.tools import dict2json, RawFormatter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        """
        cheatsheet:
        python run.py -p cfgbackup_ft_fw01.conf -d ft
        python run.py -p command_lines.txt -c -na root -ip 192.168.56.102
        """,
        formatter_class=RawFormatter
        )
    parser.add_argument("-p", "--path", type=str, required=True, help="config / command path (required)")
    parser.add_argument("-d", "--device", type=str, choices=["ft", "cp"], help="network device: ft or cp")
    parser.add_argument("-c", "--connection", action="store_true", help="send commands to the remote")
    parser.add_argument("-ip", "--ipaddress", type=str, help="remote ip address")
    parser.add_argument("-na", "--username", type=str, help="remote username")
    parser.add_argument("-pt", "--port", type=int, default=22, help="remote port")
    parser.add_argument("--password", type=str, help="remote password (unrecommanded)")
    parser.add_argument("--en-password", type=str, help="remote enable password (unrecommanded)")
    arg = parser.parse_args()

    if arg.device:
        output_path = arg.path.split(os.sep)[-1] + "_parsed.json"
        if arg.device == "ft":
            dict2json(FortiGate(arg.path).parse_policy(), output_path)
        elif arg.device == "cp":
            dict2json(CheckPoint(arg.path).parse_configuration(), output_path)
        print("save -> {}_parsed.json".format(arg.path))

    elif arg.connection:
        if not arg.ipaddress or not arg.username:
            print("Username or password not found.")
            sys.exit(-1)
        
        from network_utils.connection import Connection
        try:
            from getpass import getpass
            password = arg.password if arg.password else getpass("Password: ")
            en_password = arg.en_password if arg.en_password else getpass("Enable Password (if needed): ")
        except ImportError:
            print("Use `pip install getpass` to install the getpass requirement.")
            sys.exit(-1)

        client = Connection(ip=arg.ipaddress, username=arg.username, password=password, port=arg.port, retry=3)
        confirm_flag = {
            "'s password:": en_password,
            "Enter expert password:": en_password,
            "Are you sure you want to continue?(Y/N)[N]": "y"
        }
        print("Start receiving message:")
        print(30 * '-')
        for stdout in client.send_command_file(arg.path, confirm_flag=confirm_flag):
            print(stdout, end="")
        client.close()
