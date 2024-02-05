#!/usr/local/bin/python3

# ref: https://github.com/rthalley/dnspython/blob/master/examples/ddr.py

import sys
import argparse

import requests
import dns.resolver


def get_dns_records(domain, dns_server=["223.5.5.5", "114.114.114.114"]):
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = dns_server
    print("DNS Server: {}".format(str(dns_server)))
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


def check_website_status(domain, protocal="https", timeout=5):
    try:
        # 发送HTTP HEAD请求来检查网站状态
        response = requests.head(protocal + "://" + domain, timeout=timeout)
        return response.status_code
    except requests.exceptions.RequestException as e:
        return e


def check_bandwidth(domain, count=50):
    try:
        import ping3
    except ModuleNotFoundError as e:
        print(e)
        return None

    loss = 0
    delay = 0
    for n in range(count):
        ret = ping3.ping(domain, unit='ms', timeout=1)
        if ret is None:
            loss += 1
            continue
        delay += ret

    acc = (count - loss) * 100 / count
    loss = loss * 100 / count
    delay = delay / (count - loss)
    # TODO: 方差计算
    return f"Ping-Count: {str(count)}, Acc: {str(acc)}%, Loss: {str(loss)}%, Average-Delay: {str(delay)}ms."


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="CS: py health_check.py -d baidu.com google.com -r -s -p")
    parser.add_argument('-d', '--domains', required=True, type=str, nargs='+', help="")
    parser.add_argument('-f', '--file', action="store_true", help="Domains parameter includes path of domain file.")
    parser.add_argument('-r', '--resolve', action="store_true", help="Dns resolution.")
    parser.add_argument('-s', '--web_status', action="store_true", help="Website status code detection.")
    parser.add_argument('-p', '--ping_bandwidth', action="store_true", help="Ping bandwidth status detection.")
    arg = parser.parse_args()

    if not arg.resolve and not arg.web_status and not arg.ping_bandwidth:
        print("Invalid parameter given.")
        sys.exit(-1)
    
    DOMAINS = arg.domains
    if arg.file:
        try:
            DOMAINS = []
            for file in arg.domains:
                with open(file, 'r') as f:
                    DOMAINS += [line.strip().strip("\'\"") for line in f.readlines()]
        except Exception:
            print("Invalid file path given.")
            sys.exit(-1)

    for domain in DOMAINS:
        print(domain)
        if arg.resolve:
            ret = get_dns_records(domain)
            print(ret)
        if arg.web_status:
            ret = check_website_status(domain)
            print(ret)
        if arg.ping_bandwidth:
            ret = check_bandwidth(domain)
            print(ret)
        print()

