#!/usr/local/bin/python3
import json
import csv
import re

with open("conf/xxx.conf_parsed.json", "r") as f:
    data = json.loads(f.read())

vpn_users = data["CONFIG"]["config user local"]

with open("output.csv", "a+", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(("Name", "Status", "Email", "PasswordSetTime", "FortiToken"))

    for user in vpn_users:
        name = list(user.keys())[0][4:].strip("\" ")
        item = ' '.join(list(user.values())[0])

        status = re.search(r"set\sstatus\s\S+", item).group()[10:].strip("\" ") if re.search(r"set\sstatus\s\S+", item) else ""
        email = re.search(r"set\semail-to\s\S+", item).group()[12:].strip("\" ") if re.search(r"set\semail-to\s\S+", item) else ""
        passtime = re.search(r"set\spasswd-time\s\S+", item).group()[15:].strip("\" ") if re.search(r"set\spasswd-time\s\S+", item) else ""
        fttoken = re.search(r"set\sfortitoken\s\S+", item).group()[14:].strip("\" ") if re.search(r"set\sfortitoken\s\S+", item) else ""

        writer.writerow((name, status, email, passtime, fttoken))

