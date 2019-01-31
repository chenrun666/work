# -*- coding: utf-8 -*-
import re, paramiko, time, uuid, json, requests, os
import datetime
from PIL import ImageGrab
import random
from ftplib import FTP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import logging
from selenium.webdriver.support.ui import Select


class AirMM(object):
    logger = logging.getLogger()

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

    def get_index(self, response, browser):
        print(response)
        fromSegments = []
        fromSegmentss = {}
        passengers = []
        # driver = webdriver.Chrome(
        #     executable_path='C:\\Users\\MACHENIKE\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\chromedriver.exe')
        driver = browser
        wait = WebDriverWait(driver, 20, 3)
        name = re.findall('(.*?)/', response['name'], re.S)[0]
        password = response['pnr']
        print(name)
        print(password)
        try:
            url = 'https://ezy.flypeach.com/cn/manage/manage-authenitcate'
            driver.get(url)
            time.sleep(8)
            wait = WebDriverWait(driver, 20, 0.5)
            # pnr输入
            time.sleep(4)
            pnr_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#PNR'))).send_keys(password)
            time.sleep(1)
            # 护照输入
            passport_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#lastName'))).send_keys(name)
            time.sleep(1)
            # 点击
            submit = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#continueButton'))).click()
            time.sleep(8)

            if 'No reservation found.' and '找不到订单' not in driver.page_source:
                try:
                    # 有时候会弹出一个div框框，有时不会弹
                    small_img_close = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#ezy_popup > img'))).click()
                except:
                    pass
                try:
                    total_price = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         '#Booking-RightContent > global-basket > div > div.basket-payment-summary.clearfix > span.text-right.col-xs-6.col-md-8.l-null-padding > span'))).text
                except Exception as e:
                    msg = '当前查询单号已经飞出，请重新输入，代码108行'
                    response["taskStatus"] = 'N'
                    response["msg"] = msg
                    self.logger.error(msg)
                    return response
                num = re.findall('(\d+)', total_price, re.S)
                bag_price = ''
                for n in num:
                    bag_price += n
                result_price = int(bag_price)
                print(result_price)
                bizhong = ''
                if '¥' in total_price:
                    bizhong = 'JPY'
                else:
                    bizhong = re.findall('([A-Z]+)', total_price, re.S)
                    bizhong = bizhong[0]
                response['cur'] = bizhong

                segement = re.findall('<span class="remaining-date">(.*?)</span', driver.page_source, re.S)
                segements = re.findall('(\d+)', segement[0], re.S)
                fromSegmentss['segmentindex'] = int(segements[0])

                start_time = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#home > div:nth-child(1) > div.col-md-7 > div.col-md-12.main-details > div.cal-date > span'))).text
                start_time = re.findall('(\d+)', start_time, re.S)

                dep_time = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#home > div:nth-child(1) > div.col-md-7 > div.row.global-search-result > div:nth-child(2) > div:nth-child(1) > div > span'))).text
                dep_time_number = re.findall('(\d+)', dep_time, re.S)

                arr_time = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#home > div:nth-child(1) > div.col-md-7 > div.row.global-search-result > div:nth-child(2) > div:nth-child(3) > div > span'))).text
                arr_time_number = re.findall('(\d+)', arr_time, re.S)

                flight = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#home > div:nth-child(1) > div.col-md-5.col-xs-12.mobile-null-padding > div > div:nth-child(3) > span:nth-child(2)'))).text

                dep_times = start_time[0] + start_time[1] + start_time[2] + dep_time_number[0] + dep_time_number[1]


                # 获取到达时间：起飞具体时间和到达时间
                # start_date: ["2019", "02", "25"]
                # start_time: ["8", "25"]
                # end_time: ["8", "55"]
                arr_times = self.get_arr_time(start_date=start_time, start_time=dep_time_number, end_time=arr_time_number)

                dep_three_code = re.findall('([A-Z]+)', dep_time, re.S)
                arr_three_code = re.findall('([A-Z]+)', arr_time, re.S)
                fromSegmentss['dep'] = dep_three_code[0]
                fromSegmentss['arr'] = arr_three_code[0]
                fromSegmentss['depDate'] = dep_times
                fromSegmentss['arrDate'] = arr_times
                fromSegmentss['carrier'] = 'MM'
                fromSegmentss['flightNumber'] = 'MM' + flight
                fromSegments.append(fromSegmentss)
                # 获取订单的状态
                pnr_status = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#Booking-RightContent > global-basket > div > div.basket-payment-summary.clearfix > span.col-xs-6.col-md-4.r-null-padding'))).text
                if pnr_status == '已付款':
                    response['pnrStatus'] = 'confirm'
                else:
                    response['pnrStatus'] = pnr_status
                response['fromSegments'] = fromSegments
                time.sleep(4)
                # 获取乘客信息
                chengke_num_js = """return $("input[name='firstName']").length"""
                chengke_num = driver.execute_script(chengke_num_js)
                person = []
                genders = []
                country = []
                birthdays = []
                for i in range(chengke_num):
                    first_name_js = """return $("input[name='firstName']").eq({}).val()""".format(i)
                    last_name_js = """return $("input[name='lastName']").eq({}).val()""".format(i)
                    gender_js = """return $("select[name='Booking_Passengers_{}__Gender']").val()""".format(i)
                    country_js = """return $("select[name='Booking_Passengers_{}__Nationality'] option:selected").val()""".format(
                        i)

                    birthday_js = """return $("*[name='dob']").eq({}).val()""".format(i)
                    names = driver.execute_script(last_name_js) + '/' + driver.execute_script(first_name_js)
                    gender = driver.execute_script(gender_js)
                    guojia = driver.execute_script(country_js)
                    birthday = driver.execute_script(birthday_js)
                    person.append(names)
                    genders.append(gender)
                    country.append(guojia)
                    birthdays.append(birthday)
                for i in range(len(person)):
                    passengerss = {}
                    passengerss["name"] = person[i]
                    passengerss["gender"] = genders[i]
                    passengerss["nationality"] = country[i]
                    passengerss["birthday"] = birthdays[i].replace('/', '')
                    passengers.append(passengerss)
                response['passengers'] = passengers
                # 获取行李价格
                bag_prices = re.findall('<global-basket.*?>(.*?)</global-basket', driver.page_source, re.S)

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
                # # 获取行李信息
                bag_infor = re.findall(
                    '<div class="options">.*?<label class.*?>(.*?)<.*?<div class="extraInput selected-extra ">.*?<label.*?>(.*?)<',
                    driver.page_source, re.S)
                baggages = []

                for i in bag_infor:
                    baggagess = {}
                    if 'Additional baggage' and '托运行李' in i[1]:
                        # print i[0]
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
                        baggagess['dep'] = dep_three_code[0]
                        baggagess['arr'] = arr_three_code[0]
                        baggages.append(baggagess)
                response['baggages'] = baggages
                response["taskStatus"] = 'Y'
                response["msg"] = '成功'

                return response
            else:
                print('账号密码不匹配')
                msg = '账号密码不匹配'
                response["taskStatus"] = 'N'
                response["msg"] = msg
                self.logger.error(msg)
                return response
        except Exception as e:
            msg = '网页链接重置，可重跑'
            response["taskStatus"] = 'N'
            response["msg"] = msg
            self.logger.error(msg)
            print(e.msg)
            return response
        finally:
            print(json.dumps(response))
            driver.quit()

    def get_check_result(self, browser, req):
        result = self.get_index(req.json, browser)
        return result


if __name__ == '__main__':

    driver = webdriver.Chrome()
    obj = AirMM()
    response = {'taskStatus': None, 'id': 1494607, 'taskType': 1, 'taskSource': 1, 'taskId': 65709, 'status': 1,
                'pathStatus': 0, 'pnrStatus': '', 'msg': '', 'source': 3, 'carrier': 'MM',
                'orderCode': 'QTH_dd01bff4c1f5469bbdcde78ed58261c1', 'orderNo': 'xnm190128160142860e955f',
                'depCity': 'KIX', 'arrCity': 'HKG', 'fromDate': '2019-04-04', 'retDate': None, 'flightNumber': 'MM063',
                'tripType': 1, 'name': 'LIN/XIAOYIN', 'email': 'letaohangkong@163.com', 'accountType': '0',
                'loginAccount': None, 'loginPassword': None, 'pnr': '5CAQG6', 'price': 0.0, 'baggagePrice': 0.0,
                'cur': '', 'path': None, 'fromSegments': None, 'retSegments': None, 'passengers': None,
                'baggages': None, 'updateTime': 1548664020000, 'createTime': 1548662642000}

    obj.get_index(response, driver)
