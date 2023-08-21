#!/usr/local/bin/python3

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-2]
sys.path.append(os.sep.join(SCRIPT_DIR))

from network_utils import date_filter

out_data = pd.read_csv("互联网边界防火墙内对外下载数据.csv")
out_data["上次命中时间"] = out_data["最近命中时间"].apply(date_filter)

in_data = pd.read_csv("互联网边界防火墙外对内下载数据.csv")
in_data["上次命中时间"] = in_data["最近命中时间"].apply(date_filter)


with pd.ExcelWriter("互联网边界防火墙策略_命中统计.xlsx") as writer:
    out_data.to_excel(writer, sheet_name="内对外", index=False)
    in_data.to_excel(writer, sheet_name="外对内", index=False)

