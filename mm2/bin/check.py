import datetime
import re, json, time

import requests
from lxml import etree

from bin.log import logger
from conf.settings import *


class AirMM(object):
    def __init__(self, response):
        self.total_price = 0

        if TEST:
            self.response = TESTDATA2
        else:
            self.response = response

        self.target_url = "https://ezy.flypeach.com/cn/manage/manage-authenitcate"

        # 初始化每个模块解析的完成状态
        self.status = {
            "get_data": False,
            "parse_price": False,
            "parse_currency_type": False,
            "parse_flight_info": False,
            "parse_passenger": False,
            "parse_pnr": False,
            "parse_bag_info": False,
        }

    def get_data(self):

        lastname = self.response["name"].split("/")[0]
        pnr = self.response["pnr"]
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "referer": "https://ezy.flypeach.com/cn/manage/manage-authenitcate"
        }
        data = {
            "__RequestVerificationToken":
                "TcA2_kwuCxaNcon5xJw9zekCTCYdzEb1UD3HvEGMPM0IaqNA2ICGE0DRW7KexQmXu2qlGb9PgqdBwrxJYw3QbKaPp3434cvqhpi0ajVZ02k1",
            "PNR": pnr,
            "lastName": lastname
        }
        try:
            resp = requests.post(url=self.target_url, headers=headers, data=data, timeout=30)
            if resp.status_code == 200:
                self.content = resp.content.decode("utf-8")
                if "找不到订单" in self.content:
                    logger.info("找不到订单")
                    return
                with open("test", "w", encoding="utf-8") as f:
                    f.write(self.content)
                logger.info(f"获取任务对应信息")
                self.status["get_data"] = True
            else:
                logger.error("获取任务网络不给力")
        except Exception as e:
            logger.error(f"获取航班信息出错，错误信息为：-> {str(e)}")

    def time_dis(self, start_time, end_time):
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

    def get_arr_time(self, start_date, start_time, end_time):
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
        hour, minu = self.time_dis(start_time, end_time)

        # 转化为datetime对象
        b = datetime.timedelta(hours=hour, minutes=minu)
        arr_time = a + b

        str_time = datetime.datetime.strftime(arr_time, "%Y%m%d%H%M")
        return str_time

    def cal_age(self, timestamp):
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
            birthday = time.strftime("%Y%m%d", birthday)
            return birthday

    def parse_price(self):
        try:
            total_price = re.search(r"parseFloat\(\'(?P<num>.*?)\'\)", self.content).group("num")
            # 总价格不包含行李价格
            self.total_price = total_price
            self.response["price"] = int(total_price)
            logger.info(f"获取到总价格：{total_price}")
            self.status["parse_price"] = True
        except Exception as e:
            logger.error(f"获取总价格失败，错误信息为{str(e)}")
            self.response["taskStatus"] = "N"
            self.response["msg"] = "没有获取到对应的总价格"

    def parse_currency_type(self):
        # 匹配币种
        try:
            currency_type = re.search(r"activeCurrency: \"(?P<currency>.*?)\"", self.content)
            if currency_type:
                self.response["cur"] = currency_type.group("currency")
                logger.info("获取到支付货币的币种")
                self.status["parse_currency_type"] = True
            else:
                logger.info("获取币种失败")
        except Exception as e:
            logger.error(f"获取币种失败，错误信息是：{str(e)}")

    def parse_flight_info(self):
        fromSegments = []
        # 航班信息
        fromSegments_dic = {}

        html_etree = etree.HTML(self.content)
        try:
            segement = re.findall('<span class="remaining-date">(.*?)</span', self.content, re.S)
            segement_num = re.findall('(\d+)', segement[0], re.S)
            # 目前您预订了1航班，可在下面修改您的订单。-> 拿到航班号
            fromSegments_dic['segmentindex'] = int(segement_num[0])
            # # 出发日期
            start_time = ''.join(html_etree.xpath('//*[@id="home"]/div[1]/div[1]/div[1]/div[2]/span/text()'))
            start_time = re.findall('(\d+)', start_time, re.S)

            # 出发时间
            dep_time = ''.join(html_etree.xpath('//*[@id="home"]/div[1]/div[1]/div[2]/div[2]/div[1]/div/span/text()'))
            dep_time_number = re.findall('(\d+)', dep_time, re.S)

            # 到达时间
            arr_time = ''.join(html_etree.xpath('//*[@id="home"]/div[1]/div[1]/div[2]/div[2]/div[3]/div/span/text()'))
            arr_time_number = re.findall('(\d+)', arr_time, re.S)

            # 航班号
            flight = ''.join(html_etree.xpath('//*[@id="home"]/div[1]/div[2]/div/div[2]/span[2]/text()'))

            # 出发年月日时间
            dep_times = start_time[0] + start_time[1] + start_time[2] + dep_time_number[0] + dep_time_number[1]

            # 出发机场
            dep_flight = ''.join(
                html_etree.xpath('//*[@id="home"]/div[1]/div[1]/div[2]/div[2]/div[1]/div/span/figcaption/text()'))
            self.dep_flight = dep_flight.replace('(', '').replace(')', '')

            # 到达机场
            # //*[@id="home"]/div[1]/div[1]/div[2]/div[2]/div[3]/div/span/figcaption
            arr_flight = ''.join(
                html_etree.xpath('//*[@id="home"]/div[1]/div[1]/div[2]/div[2]/div[3]/div/span/figcaption/text()'))
            self.arr_flight = arr_flight.replace('(', '').replace(')', '')
            # 拼接到达日期
            arr_times = self.get_arr_time(start_time, dep_time_number, arr_time_number)

            fromSegments_dic['dep'] = self.dep_flight  # 起飞机场
            fromSegments_dic['arr'] = self.arr_flight  # 目的机场
            fromSegments_dic['depDate'] = dep_times  # 起飞时间
            fromSegments_dic['arrDate'] = arr_times  # 到达时间
            fromSegments_dic['carrier'] = 'MM'
            fromSegments_dic['flightNumber'] = 'MM' + flight
            fromSegments.append(fromSegments_dic)

            self.response["fromSegments"] = fromSegments
            self.response["depCity"] = self.dep_flight
            self.response["arrCity"] = self.arr_flight

            logger.info("记录航班起飞落地时间")
            self.status["parse_flight_info"] = True
        except Exception as e:
            logger.error(f"获取航班详细信息失败，错误信息是：{str(e)}")

    def parse_passenger(self):
        passengers = []

        try:
            all_passenger = re.findall(r'var passengers = JSON\.parse(.*?)\.replace', self.content)
            self.all_passenger = json.dumps(all_passenger).replace('\\', '')

            lastname = re.findall(r'"LastName":"(.*?)"', self.all_passenger)
            firstname = re.findall(r'"FirstName":"(.*?)"', self.all_passenger)
            passenger_set = {last + "/" + first for last, first in zip(lastname, firstname)}
        except Exception as e:
            passenger_set = {}
            logger.error(f"获取所有乘客信息出现错误，错误信息是{str(e)}")

        try:
            # 根据具体的乘客信息匹配到对应乘客的性别， 国籍， 生日
            for passenger_name in passenger_set:
                passenger_dic = {}
                passenger_last, passenger_first = passenger_name.split("/")
                passenger_info = re.search(
                    rf"LastName\":\"{passenger_last}\",\"FirstName\":\"{passenger_first}\".*?Date\((?P<birthday>.*?)\).*?Nationality\":\"(?P<nationality>.*?)\".*?Gender\":\"(?P<gender>.*?)\"",
                    self.all_passenger
                )

                birth = self.cal_age(passenger_info.group("birthday"))
                nationality = passenger_info.group("nationality")
                gender = passenger_info.group("gender")

                passenger_dic["name"] = passenger_name
                passenger_dic["gender"] = gender
                passenger_dic["birthday"] = birth
                passenger_dic["nationality"] = nationality

                passengers.append(passenger_dic)

            self.response["passengers"] = passengers
            self.status["parse_passenger"] = True

        except Exception as e:
            logger.error(f"获取乘客性别，国籍，生日错误，错误信息：{str(e)}")

    def parse_pnr(self):
        """
        修改票号的状态
        :return:
        """
        if self.status["get_data"]:
            self.response["pnrStatus"] = "confirm"

            logger.info("修改pnr状态为confirm")
            self.status["parse_pnr"] = True
        else:
            logger.error("修改pnrStatus失败")

    def parse_bag_info(self):
        bag_price = 0
        # 获取的乘客支付的所有项目信息
        try:
            bag_quantity_info = re.findall(r"paidServices: \[(.*?)\]", self.content)

            # 获取行李信息
            bag_infor = re.findall(
                '<div class="options">.*?<label class.*?>(.*?)<.*?<div class="extraInput selected-extra ">.*?<label.*?>(.*?)<',
                self.content, re.S)

            # 组织行李信息
            baggages = []

            # 获取乘客的行李价格
            for bag_name in bag_infor:
                baggagess = {}
                if "托运行李" in bag_name[1]:
                    bag_num = 1
                    bag_last_name, bag_first_name = bag_name[0].split()
                    baggagess["name"] = f"{bag_last_name}/{bag_first_name}"
                    passenger_bag_price = re.search(
                        rf"LastName\":\"{bag_last_name}\",\"FirstName\":\"{bag_first_name}\".*?Amount\":(?P<amount>\d+?),.*?\"Description\":\"BAGGAGE\"",
                        self.all_passenger)

                    # 获取行李的个数， 计算多个行李个数
                    bag_quantity = re.findall(r"(\d+)", bag_name[1])  # 如果没有获取到数字，就是一件行李
                    if bag_quantity:
                        # 多件行李
                        bag_num = bag_quantity[0]
                        bag_price = int(passenger_bag_price.group("amount")) * int(bag_num)
                    else:
                        # 一件行李
                        bag_price = int(passenger_bag_price.group("amount")) * int(bag_num)

                    # 计算行李的重量
                    baggageWeight = int(bag_num) * 20

                    baggagess['baggageWeight'] = baggageWeight
                    baggagess['dep'] = self.dep_flight
                    baggagess['arr'] = self.arr_flight
                    baggages.append(baggagess)

            self.response['baggages'] = baggages

            self.response["baggagePrice"] = bag_price
            # price 减去行李价格
            self.response["price"] -= bag_price

            logger.info("获取乘客的行李信息")
            self.status["parse_bag_info"] = True
        except Exception as e:
            logger.error(f"获取行李信息失败，错误信息是：{str(e)}")

        self.response["taskStatus"] = 'Y'
        self.response["msg"] = '成功'

    def modify_status(self):
        for item in self.status.values():
            if not item:
                self.response["taskStatus"] = 'N'
                self.response["msg"] = '获取信息失败'
                break
        else:
            self.response["taskStatus"] = 'Y'
            self.response["msg"] = '成功'

        logger.info(f"回填数据：{self.response}")

    def __call__(self, *args, **kwargs):
        # 获取对应的数据
        self.get_data()
        # 对获取到的数据进行解析
        self.parse_price()
        # 处理币种
        self.parse_currency_type()
        # 处理航班信息
        self.parse_flight_info()
        # 处理乘客信息
        self.parse_passenger()
        # 处理票号状态
        self.parse_pnr()
        # 处理行李信息
        self.parse_bag_info()
        # 修改任务状态
        self.modify_status()

        return self.response


if __name__ == '__main__':

    if TEST:
        # 测试环境
        # with open("../file/test", "r", encoding="utf-8") as f:
        #     recv_task = f.read()
        #     logger.debug("测试数据")

        check_data = AirMM({})
        result = check_data()
        print(json.dumps(result))

    else:
        # 线上环境
        pass
