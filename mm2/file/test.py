import time

import datetime

def cal_age(timestamp):
    """
    将时间戳转换 格式化 出生日期
    :param timestamp:
    :return:
    """
    if int(timestamp) < 0:
        # 适配windows上求解70年之前的时间
        delta = datetime.timedelta(seconds=abs(int(timestamp)) / 1000)
        timestamp_start = datetime.datetime(1970, 1, 1)
        birthday = timestamp_start - delta
        str_birthday = "".join(str(birthday).split()[0].split("-"))
        return str_birthday
    else:
        birthday = time.localtime((int(timestamp)) / 1000)
        print(birthday)
        birthday = time.strftime("%Y%m%d", birthday)
        return birthday






cal_age("-336700800000")
