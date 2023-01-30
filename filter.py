import time
import pandas as pd


def date_filter(date):
    # 判断输入日期距今是否超出 60 天

    if not date or date == "-":
        return "未命中"

    d = pd.to_datetime(date)
    n = pd.to_datetime(time.strftime("%Y.%m.%d, %H:%M:%S"))

    if abs((d-n).days) > 60:
        return "超过60天"

    return "少于60天"


if __name__ == "__main__":
    out_data = pd.read_csv("互联网边界防火墙内对外下载数据.csv")
    out_data["上次命中时间"] = out_data["最近命中时间"].apply(date_filter)

    in_data = pd.read_csv("互联网边界防火墙外对内下载数据.csv")
    in_data["上次命中时间"] = in_data["最近命中时间"].apply(date_filter)


    with pd.ExcelWriter("互联网边界防火墙策略_命中统计.xlsx") as writer:
        out_data.to_excel(writer, sheet_name="内对外", index=False)
        in_data.to_excel(writer, sheet_name="外对内", index=False)
