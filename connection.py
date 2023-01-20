#!/usr/bin/env python3

import time
import sys
import re
import getpass

try:
    import paramiko
except ImportError:
    print("paramiko is not installed, please use pip install paramiko")
    sys.exit(-1)


class Connection:
    def __init__(self, ip, username, password, port=22) -> None:
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(ip, port=port, username=username, password=password)
            self.shell= self.client.invoke_shell()
            response = self.wait_response().decode()
            # 正则捕获hostname，只能捕获网络设备
            hostname = re.compile(r"\S+[#>\]]\s*$").findall(response)
            self.hostname = hostname[0].strip().strip("<>[]#") if hostname else None
            print("Successfully login\nIP: {}\nHost name: {}".format(ip, self.hostname))
        except paramiko.AuthenticationException as e:
            print(e)
            self.client.close()
            sys.exit(-1)

    def wait_response(self, retry=10):
        attempt = 0
        while True:
            time.sleep(0.5)
            if self.shell.recv_ready() or self.shell.recv_stderr_ready():
                response = self.shell.recv(4096)
                break
            attempt += 1
            if attempt >= retry:
                response = b''
                break
        return response

    def recv_all(self, confirm_flag=None):
        output = ""
        while True:
            response = self.wait_response().decode()
            if not response:
                break
            output += response
            # 循环匹配是否出现标记字符，出现则发送确认字符
            if confirm_flag:
                confirm_word = ""
                for flag in confirm_flag:
                    if flag in response:
                        confirm_word = confirm_flag.get(flag)
                        if not isinstance(confirm_word, bytes):
                            confirm_word = bytes(confirm_word, encoding="utf-8")
                        confirm_word += b'\n'
                        self.shell.send(confirm_word)
                        break
                if confirm_word:
                    continue
            # 匹配是否出现More，出现则发送空格字符
            if "More" in response:
                self.shell.send(b"\x20")
                continue
            # 匹配是否出现hostname，出现则终止接收(有待测试)
            if re.compile(r"%s[#>\]]\s*$" %self.hostname):
                break
        return output

    def send_one_command(self, command, confirm_flag=None):
        if command[-1:] != '\n':
            command += '\n'
        command = bytes(command, encoding="utf-8")
        self.shell.send(command)
        stdout = self.recv_all(confirm_flag=confirm_flag)
        return stdout

    def send_command_file(self, command_file, confirm_flag=None):
        with open(command_file, 'r') as f:
            commands = f.readlines()
        for cmd in commands:
            yield self.send_one_command(cmd, confirm_flag=confirm_flag)

    def close(self):
        if self.client is not None:
            self.client.close()


def main():
    # ip = input("IP_ADDRESS: ")
    # username = input("username: ")
    # password = getpass.getpass("password: ")
    ip = "192.168.56.200"
    username = "admin"
    # username = "test"
    password = "1qaz2wsx"
    client = Connection(ip, username=username, password=password)

    try:
        command_file = sys.argv[1]
        confirm_flag = {
                "'s password:": "centos",
                "Enter expert password:": "1qaz2wsx",
                "Are you sure you want to continue?(Y/N)[N]": "y"
                }
        for stdout in client.send_command_file(command_file, confirm_flag=confirm_flag):
            print(stdout)
    except IndexError as e:
        print(e)
        print("no file name parameter was found, please add the parameter after the command")

    client.close()


if __name__ == "__main__":
    main()


