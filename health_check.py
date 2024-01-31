#!/usr/local/bin/python3

# ref: https://github.com/rthalley/dnspython/blob/master/examples/ddr.py

import requests
import dns.resolver
import pandas as pd
from tqdm import tqdm


def get_dns_records(domain):
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = ["114.114.114.114", "8.8.8.8"]
    res.try_ddr()
    ANSWER = {"A": [], "CNAME": []}

    try:
        for rr in res.resolve(domain, "A"):
            ANSWER["A"].append(rr.address)
    except Exception:
        pass
    try:
        for rr in res.resolve(domain, "CNAME"):
            ANSWER["CNAME"].append(rr.__str__())
    except Exception:
        pass
    return ANSWER


def check_website_status(protocal, domain, timeout=5):
    try:
        # 发送HTTP HEAD请求来检查网站状态
        response = requests.head(protocal + "://" + domain, timeout=timeout)
        return response.status_code
    except requests.exceptions.RequestException as e:
        return e


if __name__ == "__main__":
    pass

