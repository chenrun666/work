import datetime


# 计算时间差
import json


def time_dis(start_time, end_time):
    """
    给定小时和分钟数，计算相差时间是多少
    :param start_time:
    :param end_time:
    :return: 返回相差时间的小时和分钟数
    """
    hour = int(end_time[0]) - int(start_time[0])
    minu = int(end_time[1]) - int(start_time[1])

    if hour < 0 and minu >= 0:
        hour = 24 + hour
    elif hour < 0 and minu <= 0:
        hour = 23 + hour
        minu = minu + 60
    elif hour > 0 and minu <= 0:
        minu = minu + 60
        hour -= 1

    return hour, minu


def get_arr_time(start_date, start_time, end_time):
    """
    获取到达时间：起飞具体时间和到达时间
    :start_date: ["2019", "02", "25"]
    :start_time: ["8", "25"]
    :end_time: ["8", "55"]
    :return: 返回时间字符串： "201902250855"
    """
    # 将起飞时间转换为datetime对象
    a = datetime.datetime(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]),
                          hour=int(start_time[0]), minute=int(start_time[1]))

    # 计算时间差
    hour, minu = time_dis(start_time, end_time)

    # 转化为datetime对象
    b = datetime.timedelta(hours=hour, minutes=minu)
    arr_time = a + b

    str_time = datetime.datetime.strftime(arr_time, "%Y%m%d%H%M")
    print(arr_time)
    return str_time


start_date = ["2019", "02", "25"]
start_time = ["08", "30"]

end_time = ["01", "20"]

get_arr_time(start_date, start_time, end_time)

if __name__ == '__main__':
    import copy
    birthday = ["215740800000", "275443200000", "215740800000", "275443200000", "1", "2", "1", "2"]
    copy_brithday = copy.deepcopy(birthday)

    for i in birthday:
        if copy_brithday.count(i) > 1:
            copy_brithday.remove(i)

    print(copy_brithday)










