import copy
import uuid
import logging
import datetime
import re, json, time

import requests

from lxml import etree

# http://47.92.39.84:9444/resultTask?traceID=(uuid)  回填接口
# http://47.92.39.84:9444/sendTasks?carrier=MM&traceID=065de17a-fafb-11e8-8eb2-f2801f1b9fd1  任务接口


# 初始化日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(filename=f'./mm_log.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


class AirMM(object):

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

    def get_index(self, response):
        # 测试状态
        test_flag = True

        # 测试数据

        response =     {'taskStatus': None, 'id': 1475140, 'taskType': 1, 'taskSource': 1, 'taskId': 61286, 'status': 1, 'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 2, 'carrier': 'MM', 'orderCode': 'CTR_ebf14bd694024ea881fc75fdcdaa66ff', 'orderNo': '389936026', 'depCity': 'KIX', 'arrCity': 'PUS', 'fromDate': '2019-02-21', 'retDate': None, 'flightNumber': 'MM017', 'tripType': 1, 'name': 'AN/JUNHYEON', 'email': 'letaohangkong@163.com', 'accountType': '0', 'loginAccount': None, 'loginPassword': None, 'pnr': 'Y98457', 'price': 0.0, 'baggagePrice': 0.0, 'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None, 'baggages': None, 'updateTime': 1548330704000, 'createTime': 1548330704000}


        # 记录日志，领取到的任务
        logging.info(f"获取到任务{response}")
        print("获取到任务：-> " + str(response))

        # 获取数据放置到data
        lastname = response["name"].split("/")[0]
        pnr = response.get("pnr")

        fromSegments = []
        # 航班信息
        fromSegmentss = {}
        passengers = []
        # 目标连接
        url = "https://ezy.flypeach.com/cn/manage/manage-authenitcate"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "referer": "https: // ezy.flypeach.com / cn / manage / manage - authenitcate",
            "connection": "close"
        }
        data = {
            "__RequestVerificationToken": "v5OzxAwaJKpYE_-_JbMq6DvpoUF7L4h7og3y1EAfgBZTrQAMkn0xF0NdLx-tgZDrx1W5b_7IwEiXETXKVloIDEzlCJxRlLc-dbraJT7wx2I1",
            "PNR": pnr,
            "lastName": lastname,
        }
        if test_flag:
            # with open("./test", "r", encoding="utf-8") as f:
            #     content = f.read()
            resp = requests.post(url=url, headers=headers, data=data)
            content = resp.content.decode("utf-8")
            with open("test", "w", encoding="utf-8") as f:
                f.write(content)

        else:
            resp = requests.post(url=url, headers=headers, data=data)
            content = resp.content.decode("utf-8")
            with open("test", "w", encoding="utf-8") as f:
                f.write(content)

        html_etree = etree.HTML(content)
        if 'No reservation found.' and '找不到订单' not in content:
            try:
                # 获取总价
                total_price = re.search(r"parseFloat\(\'(?P<num>.*?)\'\)", content).group("num")
                # print(total_price)
            except Exception as e:
                msg = '没有获取到pnr号'
                response["taskStatus"] = 'N'
                response["msg"] = msg
                logging.error(msg)
                return response

            num = re.findall('(\d+)', total_price, re.S)
            bag_price = ''
            for n in num:
                bag_price += n
            result_price = int(bag_price)
            # 匹配币种
            currency_type = re.search(r"activeCurrency: \"(?P<currency>.*?)\"", content)

            if currency_type:
                response["cur"] = currency_type.group("currency")

            segement = re.findall('<span class="remaining-date">(.*?)</span', content, re.S)
            segements = re.findall('(\d+)', segement[0], re.S)
            # 目前您预订了1航班，可在下面修改您的订单。-> 拿到航班号
            fromSegmentss['segmentindex'] = int(segements[0])
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
            dep_flight = dep_flight.replace('(', '').replace(')', '')

            # 到达机场
            arr_flight = ''.join(
                html_etree.xpath('//*[@id="home"]/div[1]/div[1]/div[2]/div[2]/div[3]/div/span/figcaption/text()'))
            arr_flight = arr_flight.replace('(', '').replace(')', '')
            # 拼接到达日期
            arr_times = self.get_arr_time(start_time, dep_time_number, arr_time_number)

            fromSegmentss['dep'] = dep_flight  # 起飞机场
            fromSegmentss['arr'] = arr_flight  # 目的机场
            fromSegmentss['depDate'] = dep_times  # 起飞时间
            fromSegmentss['arrDate'] = arr_times  # 到达时间
            fromSegmentss['carrier'] = 'MM'
            fromSegmentss['flightNumber'] = 'MM' + flight
            fromSegments.append(fromSegmentss)

            # 获取乘客信息
            all_list = re.findall(r'var passengers = JSON\.parse(.*?)\.replace', content)
            all_list = json.dumps(all_list).replace('\\', '')

            lastname = re.findall(r'"LastName":"(.*?)"', all_list)
            firstname = re.findall(r'"FirstName":"(.*?)"', all_list)

            names = []
            births = []
            for last_name, first_name in zip(lastname, firstname):
                names.append(last_name + "/" + first_name)
            # 赋值一个names列表，列表循环的时候不要删除列表內的值
            new_names = copy.deepcopy(names)
            # 去重，遇到重名会有bug
            for i in new_names:
                if names.count(i) > 1:
                    names.remove(i)

            # 获取对应的生日
            for name in names:
                birth_last_name, birth_first_name = name.split("/")
                # 获取对应的生日
                birth_re = re.findall(
                    rf"LastName\":\"{birth_last_name}\",\"FirstName\":\"{birth_first_name}\".*?Date\((\d+?)\)",
                    all_list)
                birth = time.localtime(int(birth_re[0]) / 1000)
                birth = time.strftime("%Y%m%d", birth)
                births.append(birth)

            # 国籍
            nationality = re.findall(r'"Nationality":"(?P<nationality>.*?)"', all_list)

            # 性别
            gender = re.findall(r'"Gender":"(?P<gender>.*?)"', all_list)

            for i in range(len(gender)):
                passengerss = {}
                passengerss["name"] = names[i]
                passengerss["gender"] = gender[i]
                passengerss["birthday"] = births[i]
                passengerss["nationality"] = nationality[i]
                passengers.append(passengerss)
            response['passengers'] = passengers

            # 凡是通过票号能查到的单子，都是已经付款了的
            response['pnrStatus'] = 'confirm'
            response['fromSegments'] = fromSegments

            # 获取行李价格
            bag_prices = re.findall('<global-basket.*?>(.*?)</global-basket', content, re.S)

            if 'Add Bags' in str(bag_prices):
                uls = re.findall('<ul data-bind="foreach: adultExtras">(.*?)</ul', str(bag_prices), re.S)
                price_set = re.findall('<div class="section-cell" data-bind="text: displayPrice">(.*?)<', str(uls),
                                       re.S)
                prices = re.findall('(\d+)', price_set[0].replace('\\\\xa5', ''), re.S)
                str2 = ''
                for s in prices:
                    str2 += s
                bag_price = int(str2)
                response['baggagePrice'] = bag_price
            else:
                bag_price = 0
                response['baggagePrice'] = bag_price

            response['price'] = result_price - int(bag_price)

            # 获取行李信息
            bag_infor = re.findall(
                '<div class="options">.*?<label class.*?>(.*?)<.*?<div class="extraInput selected-extra ">.*?<label.*?>(.*?)<',
                content, re.S)
            # print(bag_infor)
            baggages = []

            for i in bag_infor:
                baggagess = {}
                if 'Additional baggage' and '托运行李' in i[1]:
                    # print(i[0])
                    name = i[0].split()
                    name.reverse()
                    name = "{0}/{1}".format(name.pop(), ''.join(name))
                    baggagess['name'] = name
                    weight = re.findall('(\d+)', i[1], re.S)
                    baggageWeight = 0
                    if weight == []:
                        weight = 1
                        baggageWeight = weight * 20
                    baggagess['baggageWeight'] = baggageWeight
                    baggagess['dep'] = dep_flight
                    baggagess['arr'] = arr_flight
                    baggages.append(baggagess)
                response['baggages'] = baggages
                response["taskStatus"] = 'Y'
                response["msg"] = '成功'

            response = json.dumps(response)

            print(response)
            logging.info("回填数据 -> " + str(response))
            return response


        else:
            print('账号密码不匹配')
            msg = '账号密码不匹配'
            response["taskStatus"] = 'N'
            response["msg"] = msg
            logging.info(msg)
            return response


if __name__ == '__main__':
    air = AirMM()
    back_fill_url = "http://47.92.39.84:9444/resultTask?traceID=" + str(uuid.uuid4())
    interface_url = "http://47.92.39.84:9444/sendTasks?carrier=MM&traceID=065de17a-fafb-11e8-8eb2-f2801f1b9fd1"

    # while True:
    #     response = requests.get(interface_url).json().get("data")
    #     if response:
    #         back_response = air.get_index(response[0])
    #         # 将数据返回数据接口
    #         try:
    #             back_fill_back = requests.post(url=back_fill_url, data=back_response,
    #                                            headers={"content-type": "application/json"})
    #             logging.info("回填状态 -> " + back_fill_back.text)
    #         except Exception as e:
    #             logging.info("回填出错 ->" + str(e))
    #     else:
    #         print(f"{time.time()} -> 没有数据, 等待10秒")
    #         time.sleep(10)

    air.get_index({})

