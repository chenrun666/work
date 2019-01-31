import datetime
import time

# def calculation_luggage(baggageweight):
#     """
#     baggageweight:目标行李的重量
#     根据行李的重量，分配行李的选择方式
#     选择行李分为两个档次，一个是23KG，25块钱。一个是32KG，75块钱
#     :param baggageweight:
#     :return: 返回选择几个23KG和几个32KG
#     """
#     select_times = {"23": 0, "32": 0}
#     # 100KG, 首先用目标重量小于32除23，如果结果小于1那么就选择一个23，
#
#     if 32 < baggageweight <= 46:
#         select_times["23"] = 2
#
#     elif baggageweight <= 32 or 46 < baggageweight <= 142:
#         s, y = divmod(baggageweight, 55)
#         select_times["23"] = s
#         select_times["32"] = s
#         if y == 0:
#             pass
#         elif 0 < y <= 23:
#             select_times["23"] += 1
#         elif 23 < y <= 32:
#             select_times["32"] += 1
#         else:
#             select_times["23"] += 1
#             select_times["32"] += 1
#     elif 142 < baggageweight <= 151:
#         select_times["23"] = 1
#         select_times["32"] = 4
#     else:
#         select_times["23"] = 0
#         select_times["32"] = 5
#
#     return select_times["23"], select_times["32"]
#
#
# time1 = "201902011320"
#
# year = time1[0:4]
# month = time1[4:6]
# day = time1[6:8]
# hour = time1[8:10]
# minu = time1[10:12]
#
# print(year, month, day, hour, minu)
#
#
# money = "1,534.34"
# import re
#
# money1 = re.findall(r"[\d+.]+", money)
# print(money1)


li = [1, 2, 3, 6]
target = 9


def func():
    d = {}
    for i, item in enumerate(li):
        tmp = target - item

        for key, value in d.items():
            if tmp == value:
                return [key, i]
        d[i] = item

    return None

print(func())
