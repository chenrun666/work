# # -*- coding: utf-8 -*-
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import requests
import json
from xml import etree


class EnuCrawl:

    def __init__(self, password=u'jiushini123', dep='Agadir', arr='Austria', depDate='2019-01-23'):
        # 姓名
        self.name = 'CHO/YOOJIN'
        # 登录的密码
        self.password = password
        # 起始出发地
        self.dep = dep
        # 到达目的地
        self.arr = arr
        # 出发时间
        self.depDate = depDate

        # 获取接口数据请求函数

    def get_task(self):
        pass
        # try:
        #     data = {'Content-Type': 'application/json'}
        #     req_url = ''
        #     headers = {
        #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        #         'Content-Type': 'application/json'}
        #     data = json.dumps(data)
        #     response = requests.post(url=req_url, headers=headers, data=data)
        #     response.encoding = response.apparent_encoding
        #     data = response.text
        #     print(data)
        # except Exception as e:
        #     print(e)

    # 填写回调函数
    # def back_task(self):
    #     data = {}
    #     headers = {
    #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    #         'Content-Type': 'application/json'
    #     }
    #     # 回调url
    #     req_url = ''
    #     response = requests.post(url=req_url,headers=headers,data=data)
    #     response.encoding = response.apparent_encoding
    #     data = response.text
    #     return data

    # 网站语言为德语或者英语，如果是德语的话直接点击修改成英语
    def is_language(self):
        # 判断语言是否为英语
        # language_English = WebDriverWait(self.drive,50).until(EC.presence_of_element_located(
        #     (By.XPATH('//div[@class="nav-main-list"]/a[1]'))))
        language_English = self.drive.find_element_by_xpath('//div[@class="nav-main-list"]/a[1]').text
        if language_English == 'German':
            pass
        else:
            WebDriverWait(self.drive, 50).until(EC.presence_of_element_located(
                By.XPATH('//*[@class="nav-main-list"]/a[1]')))
            self.drive.find_element_by_xpath('//*[@class="nav-main-list"]/a[1]').click()

    def login(self):
        # option = 'C:\Program Files\Chrome\chromedriver.exe'
        # self.drive = webdriver.Chrome(executable_path=option)
        self.drive = webdriver.Chrome()
        # 窗口最大化
        self.drive.maximize_window()
        # 登录url网址
        self.drive.get('https://mobile.eurowings.com/booking/Select.aspx?culture=en-GB')

    # 点击去登陆按钮
    #  WebDriverWait(self.drive,20).until(EC.presence_of_element_located(
    #      (By.XPATH,'//span[@class="icon-menu"]')))
    #  self.drive.find_element_by_xpath('//span[@class="icon-menu"]/..').click()
    #  # 更改语言为英语
    #  # self.is_language()
    #  # 等待login登录按钮显示出来
    #  WebDriverWait(self.drive,50).until(EC.presence_of_element_located(
    #      (By.XPATH,'//*[@class="login-form-head"]/span[2]')))
    #  self.drive.find_element_by_xpath('//*[@class="login-form-head"]/span[2]').click()
    #  # 等待用户名和密码框出现
    #  WebDriverWait(self.drive,50).until(EC.presence_of_element_located(
    #      (By.XPATH,'//span[@class="footer-icon icon-ico-arrow-close"]')))
    #  # 输入用户名
    #  self.drive.find_element_by_xpath('//input[@id="user"]').send_keys(self.username)
    #  # 输入密码
    #  self.drive.find_element_by_xpath('//input[@id="password"]').send_keys(self.password)
    #  # 等待输入用户名成功的提示
    #  WebDriverWait(self.drive,20).until(EC.presence_of_element_located(
    #      By.XPATH('//div[@class="input-box link valid"][1]')))
    #  # 等待密码属于成功的提示
    #  WebDriverWait(self.drive, 20).until(EC.presence_of_element_located(
    #      By.XPATH('//div[@class="input-box link valid"][2]')))
    #  # 点击登录
    #  self.drive.find_element_by_xpath('//*[@id="loginUser"]').click()

    # 属于航班信息，出发机场、目的地、出发时间、返回日期
    def select_fight(self, depAirport, arrAirport, dep_date, Adult, Children, Infants):
        # 选择方式为单程
        WebDriverWait(self.drive, 30).until(EC.presence_of_element_located((
            By.XPATH, ('//*[@class="tabcontainer col2"]/label[2]'
                       ))))
        self.drive.find_element_by_xpath('//*[@class="tabcontainer col2"]/label[2]').click()
        time.sleep(3)
        # 等待出发机场加载
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH, ('//span[contains(text(),"Departure airport")]'
                       ))))
        self.drive.find_element_by_xpath('//span[contains(text(),"Departure airport")]').click()
        # 点击出发机场
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH, ('//*[@class="suggestions"]/ul[2]/li[1]/span/..'
                       ))))
        time.sleep(3)
        # dep_script = 'document.getElementById("SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_Origin").value="Basel";'
        # print(dep_script)
        # time.sleep(5)
        # self.drive.execute_script(dep_script)
        self.drive.find_element_by_xpath('//*[@class="input-icon-wrapp"]/input').send_keys(depAirport)
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH, ('//*[@class="suggestions"]/ul[2]/li[5]'
                       ))))
        self.drive.find_element_by_xpath('//*[@class="suggestions"]/ul[2]/li[5]').click()
        time.sleep(5)
        # 点击到达机场
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH, ('//span[contains(text(),"Arrival airport")]'))))
        # arr_script = 'document.getElementById("SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_Destination").value="Basel";'
        # time.sleep(5)
        # print(arr_script)
        # self.drive.execute_script(arr_script)
        self.drive.find_element_by_xpath('//span[contains(text(),"Arrival airport")]').click()
        WebDriverWait(self.drive, 80).until(
            EC.presence_of_element_located((By.XPATH, ('//*[@class="input-icon-wrapp"]/input'))))
        time.sleep(5)
        self.drive.find_element_by_xpath(
            '//div[starts-with(@class,"fly-up search-airport-destination")]/div[3]/div/input').send_keys(arrAirport)
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located(
            (By.XPATH, ('//div[starts-with(@class,"fly-up search-airport-destination")]/div[4]/ul/li[5]'))))
        self.drive.find_element_by_xpath(
            '//div[starts-with(@class,"fly-up search-airport-destination")]/div[4]/ul/li[5]').click()
        time.sleep(5)
        # 点击出发日期
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH, ('//*[@id="departuredate"]/span[2]'))))
        # self.drive.find_element_by_xpath('//*[@id="departuredate"]/span[2]').click()
        # WebDriverWait(self.drive,80).until(EC.presence_of_element_located((By.XPATH,('//*[@data-year="{}"][@data-month="{}"]/a[text()="{}"]/..'.format(self.depDate[:4],int(self.depDate[5:7]) - int(dep_date[5:7]),self.depDate[-2:])))))
        # self.drive.find_element_by_xpath('//*[@data-year="{}"][@data-month="{}"]/a[text()="{}"]/..'.format(self.depDate[:4],int(self.depDate[5:7]) - int(dep_date[5:7]),self.depDate[-2:])).click()
        time.sleep(5)
        depdata_script = 'document.getElementById("SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_departureDate").value="{}";'.format(
            dep_date)
        self.drive.execute_script(depdata_script)
        # 点击出行人数
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="travellers"]'))))
        adult_script = 'document.getElementById("SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_Adults").value="{}";'.format(
            Adult)
        self.drive.execute_script(adult_script)
        children_script = 'document.getElementById("SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_Childs").value="{}";'.format(
            Children)
        self.drive.execute_script(children_script)
        # 如果乘客有婴儿，手动出单
        if Infants > 0:
            print('乘客中有婴儿，需手动出单')
            errorMsg = "出现婴儿票，请人工处理"
            # status = payFail
            # result["status"] = status
            # result["errorMessage"] = errorMsg
        else:
            infants_script = 'document.getElementById("SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_Infants").value="0";'
            self.drive.execute_script(infants_script)
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((By.XPATH, (
            '//button[@id="SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_ButtonSubmit"]'))))
        self.drive.find_element_by_xpath(
            '//button[@id="SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_ButtonSubmit"]').click()

    # 航班信息价格
    def airport_info(self, targetPrice, depAirport, arrAirport, ):
        # 等待航班信息加载完成
        try:
            WebDriverWait(self.drive, 50).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="flight-wrapper"]')))
        except:
            errorMsg = "航班信息不存在"
            print('航班信息有误')
        else:
            WebDriverWait(self.drive, 50).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a')))
            # 航班号
            depFlightNumber = self.drive.find_element_by_xpath(
                '//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a/div/div[3]/div/div[1]').text.encode('utf-8')
            print(depFlightNumber, 'depFlightNumber')
            price = self.drive.find_element_by_xpath(
                '//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a/div/div[2]/div[2]').text.encode('utf-8')
            price = re.findall(r'[0-9.]+', price)
            arr_dep_Airport = self.drive.find_element_by_xpath(
                '//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a/div/div/div[1]').text.encode('utf-8')
            if float(targetPrice) > float(price[0]):
                if depAirport == arr_dep_Airport.split(' ')[0] and arrAirport == arr_dep_Airport.split(' ')[1]:
                    # ActionChains(self.drive).move_to_element(
                    #     '//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a').click()
                    self.drive.find_element_by_xpath('//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a/.').click()
                else:
                    errorMsg = '您输入的出发地和目的地有误'
                    print('您输入的出发地和目的地有误')
            else:
                errorMsg = '航班价格大于目标价格'

        # 航班时间
        time = self.drive.find_element_by_xpath(
            '//div[@id="siteContent"]/div/div[2]/div[3]/div[2]/a/div/div[2]/div[1]').text.encode('utf-8')
        print(time, 'time')

        # 获取航班信息
        # WebDriverWait(self.drive).until(EC.presence_of_element_located((
        #     By.XPATH,('//div[starts-with(@class,"flight-wrapper")]/..'
        # ))))
        # 出发时间
        # Airport_date = self.drive.find_element_by_xpath('//div[starts-with(@class,"start-time valignMiddle")]').is_displayed()
        # print(Airport_date,'Airport_date',type(Airport_date))
        # # 机票价格
        # Airport_price = self.drive.find_element_by_xpath('//div[starts-with(@class,"flight-wrapper")]/div[2]/div[2]/span').text
        # print(Airport_price,'Airport_price')
        # # 航班号
        # Airport_port = self.drive.find_element_by_xpath('//div[starts-with(@class,"flight-wrapper")]/div[3]/div/div').text
        # print(Airport_port,'Airport_port')
        # # 点击航班信息
        # fight_info = self.drive.find_element_by_xpath('//*[@id="siteContent"]/div/div[2]/div[3]').text
        # print(fight_info)
        # WebDriverWait(self.drive,80).until(EC.presence_of_element_located((By.XPATH,('//*[@id="siteContent"]/div/div[2]/div[3]'))))
        # fight_price = self.drive.find_element_by_xpath('//*[@id="siteContent"]/div/div[2]/div[3]').text
        # print(fight_price,type(fight_price))
        # 点选SMART航班信息
        WebDriverWait(self.drive, 80).until(
            EC.presence_of_element_located((By.XPATH, ('//span[contains(text(),"SMART")]'))))
        self.drive.find_element_by_xpath('//span[contains(text(),"SMART")]').click()
        # 点选下一步
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located(
            (By.XPATH, ('//button[@id="SelectViewControlGroupFlightSelection_ButtonSubmit"]'))))
        self.drive.find_element_by_xpath('//button[@id="SelectViewControlGroupFlightSelection_ButtonSubmit"]').click()

        # 订单总价格
        subtotal_price = self.drive.find_element_by_xpath('//div[@id="priceBox"]/div/span/span[3]').text
        subtotal_price = subtotal_price[1:]
        # 点选booking_fight
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located(
            (By.XPATH, ('//button[@id="ServicesOverviewViewControlGroup_ButtonSubmit"]'))))
        self.drive.find_element_by_id('#ServicesOverviewViewControlGroup_ButtonSubmit').click()

    # 填写乘客信息
    def fill_passenger(self, name):
        # 填写乘客信息
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH,
            ('//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$firstname1"]'
             ))))
        self.drive.find_element_by_xpath(
            '//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$firstname1"]').send_keys(
            name.split('/')[0])
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH,
            '//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$lastname1"]'
        )))
        self.drive.find_element_by_xpath(
            '//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$lastname1"]').send_keys(
            name.split('/')[1])

        WebDriverWait(self.drive, 80).until(
            EC.presence_of_element_located((By.XPATH, '//input[@data-datepart="birthdate_day"]')))
        self.drive.find_element_by_xpath('//input[@data-datepart="birthdate_day"]').send_keys()

        # 输入手机号
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH,
            '//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$mobilephone1"]'
        )))
        self.drive.find_element_by_xpath(
            '//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$mobilephone1"]').send_keys(
            '18810298353')
        # 输入邮箱
        WebDriverWait(self.drive, 80).until(EC.presence_of_element_located((
            By.XPATH,
            '//input[@name="PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$email1"]'
        )))
        self.drive.find_element_by_xpath(
            'PassengerViewControlGroupPassengerInput$PassengerViewPassengerInputControl$email1').send_keys(
            '807028612@qq.com')

        # 点击提交data
        WebDriverWait(self.drive).until(EC.presence_of_element_located((
            By.XPATH, '//button[@id="PassengerViewControlGroupPassengerInput_ButtonSubmit"]'
        )))
        self.drive.find_element_by_xpath('//button[@id="PassengerViewControlGroupPassengerInput_ButtonSubmit"]').click()

    def girl_select(self):
        # 如果是女孩则点击
        girl_script = 'document.getElementById("PassengerViewControlGroupPassengerInput_PassengerViewPassengerInputControl_title1{}Female").value="{}";'.format(
            '1', 'MRS')
        self.drive.execute_script(girl_script)

    # 确认发票信息
    def invoice_data(self):
        pass

        # # 添加行李
        # def booking_luggage(self):
        #     # 获取座位信息
        #
        #     WebDriverWait(self.drive,80).until(EC.presence_of_element_located((By.XPATH,('//a[@href="Baggage.aspx"]'))))
        #     self.drive.find_element_by_xpath('//a[@href="Baggage.aspx"]').click()
        #     booking_row_script = 'document.getElementById("SeatSelection_Flight_1_Pax_0_SeatRow").value="{}";'.format(1)
        #     self.drive.execute_script(booking_row_script)
        #     booking_columns_script = 'document.getElementById("SeatSelection_Flight_1_Pax_0_SeatColumn").value="{}";'.format("c")
        #     self.drive.execute_script(booking_columns_script)

    # 判断出发日期是否有效
    def dep_date(self, depDate):
        dep_date = datetime.datetime.now().strftime('%Y-%m-%d')
        if depDate >= dep_date:
            return depDate
        else:
            print('您输入的出发时间有误')
            return

    # 根据出生日期计算年龄
    def calculate_age(self, birthday):
        today = datetime.date.today()
        birthday = datetime.date(*map(int, birthday.split('-')))
        try:
            birthday = birthday.replace(year=birthday.year)
        except ValueError:
            birthday = birthday.replace(year=today.year, day=birthday.day - 1)
        if birthday > today:
            return today.year - birthday.year - 1
        else:
            return today.year - birthday.year

    def start(self):
        # 登录
        self.login()
        # 获取接口数据
        # self.get_task()
        # 读取测试数据
        with open("test.json", 'r') as f:
            request_data = json.loads(f.read())
            depAirport = request_data['depAirport']
            arrAirport = request_data['arrAirport']
            depDate = request_data['depDate']
            passengerCount = request_data['passengerCount']
            targetPrice = request_data['targetPrice']
            name = request_data['passengerVOList'][0]['name']
            print(name)
        Adult = 0
        Children = 0
        Infants = 0
        for data in request_data['passengerVOList']:
            if int(passengerCount) == len(request_data['passengerVOList']):
                birthday = data['birthday']
                age = self.calculate_age(birthday)
                if age > 12:
                    Adult += 1
                elif 2 > age > 12:
                    Children += 1
                else:
                    Infants += 1
            else:
                errorMsg = "乘客人数有误"

        # 判断出发时间是否有效
        dep_date = self.dep_date(depDate)
        # 点击选择出发机场、到达机场，到达时间
        self.select_fight(depAirport, arrAirport, dep_date, Adult, Children, Infants)
        # 页面刷新再次执行
        self.drive.refresh()
        self.select_fight(depAirport, arrAirport, dep_date, Adult, Children, Infants)
        # 选取航班号
        self.airport_info(targetPrice, depAirport, arrAirport, )
        # # 回填数据
        # self.back_task()
        # 选择航班信息
        # self.select_fight()
        # # 填写信息
        # self.airport_info()
        # # 填写乘客信息
        # self.fill_passenger()


if __name__ == '__main__':
    en = EnuCrawl()
    en.start()
