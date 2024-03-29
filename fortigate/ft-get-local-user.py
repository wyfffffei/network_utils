#!/usr/local/bin/python3
import json
import csv
import re

with open("conf/xxx.conf_parsed.json", "r") as f:
    data = json.loads(f.read())

vpn_users = data["CONFIG"]["config user local"]
vpn_group = data["CONFIG"]["config user group"]

# NEW: take vpn group dict
GROUPS = {}
for group in vpn_group:
    group_name = list(group.keys())[0].split(" ")[-1].strip("\"")
    members = list(group.values())[0]

    if not members:
        continue

    members = members[0][11:].split(" ")
    for member in members:
        member = member.strip("\"")
        if not GROUPS.get(member):
            GROUPS[member] = group_name
        else:
            GROUPS[member] += (", " + group_name)

# for key, value in GROUPS.items():
#     print(key, end="\t")
#     print(value)

with open("output.csv", "a+", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(("Name", "Group", "Status", "Email", "PasswordSetTime", "FortiToken"))

    for user in vpn_users:
        name = list(user.keys())[0][4:].strip("\" ")
        item = ' '.join(list(user.values())[0])

        group = GROUPS.get(name) if GROUPS.get(name) else ""
        status = re.search(r"set\sstatus\s\S+", item).group()[10:].strip("\" ") if re.search(r"set\sstatus\s\S+", item) else ""
        email = re.search(r"set\semail-to\s\S+", item).group()[12:].strip("\" ") if re.search(r"set\semail-to\s\S+", item) else ""
        passtime = re.search(r"set\spasswd-time\s\S+", item).group()[15:].strip("\" ") if re.search(r"set\spasswd-time\s\S+", item) else ""
        fttoken = re.search(r"set\sfortitoken\s\S+", item).group()[14:].strip("\" ") if re.search(r"set\sfortitoken\s\S+", item) else ""

        writer.writerow((name, group, status, email, passtime, fttoken))

