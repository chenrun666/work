"""
目标url: https://mobile.eurowings.com/booking/Search.aspx?culture=en-GB
1， 登陆
2， 根据获取到的数据选择航班信息乘客信息
3， 点击完成购买
"""
from bin.purchase import FillFlightInfo
from bin.get_task import *


if __name__ == '__main__':
    if TEST:
        with open("../file/test.json", "r", encoding="utf-8") as f:
            recv = json.loads(f.read())
            if recv["success"]:
                task = recv["data"]
            else:
                task = recv["data"]
    else:
        # 访问接口获取任务数据
        task = json.loads(get_task())

    fill_flight_info = FillFlightInfo(task)
    # 执行__call__方法
    backdata = fill_flight_info()
    print(backdata)
    # 回填数据
    back_fill(backdata)



