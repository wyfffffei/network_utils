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
        python run.py -p english_words.txt -t path_of_key.txt  (translator)
        python run.py -p cfgbackup_ft_fw01.conf -d ft  (config parser)
        python run.py -p command_lines.txt -i 192.168.56.102 -u root (command sender)
        """,
        formatter_class=RawFormatter
        )
    parser.add_argument("-p", "--path", type=str, required=True, help="english words / config / command path (required)")
    parser.add_argument("-t", "--translate", type=str, help="secretkey file path(content: 'appid,secretkey'), translate file line-by-line")
    parser.add_argument("-d", "--device", type=str, choices=["ft", "cp"], help="network device: ft or cp")
    parser.add_argument("-i", "--ipaddress", type=str, help="remote ip address")
    parser.add_argument("-u", "--username", type=str, help="remote username")
    parser.add_argument("--port", type=int, default=22, help="remote port")
    parser.add_argument("--password", type=str, help="remote password (unrecommanded)")
    parser.add_argument("--en-password", type=str, help="remote enable password (unrecommanded)")
    arg = parser.parse_args()

    if arg.translate:
        from network_utils.translator import Baidu_Translator
        try:
            with open(arg.translate, "r", encoding="utf-8") as f:
                appid, secretKey = f.readlines()[0].strip().split(",")
        except Exception as e:
            print(e)
            print("secretkey file is invalid")
            sys.exit(-1)
        bt = Baidu_Translator(appid, secretKey)
        res = bt.translate_file(arg.path, is_save=True)
        with open(arg.path.split(os.sep)[-1] + "_translated.txt", "w", encoding="utf-8") as f:
            f.writelines([w + "\n" for w in res])

    elif arg.device:
        output_path = arg.path.split(os.sep)[-1] + "_parsed.json"
        if arg.device == "ft":
            dict2json(FortiGate(arg.path).parse_policy(), output_path)
        elif arg.device == "cp":
            dict2json(CheckPoint(arg.path).parse_configuration(), output_path)
        print("save -> {}_parsed.json".format(arg.path))

    elif arg.ipaddress:
        if not arg.username:
            print("Username not found.")
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
        for stdout in client.send_command_file(arg.path, confirm_flag=confirm_flag):
            print(stdout, end="")
        client.close()

