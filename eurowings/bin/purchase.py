"""
完成选择乘客，点击购买的操作，使用selenium
流程：
1，填写航班信息查询机票，选择机票 ---> 2，选择行李 ---> 3，填写乘客信息 ---> 4，填写发票信息 ---> 5，填写支付信用卡信息
"""
import re
import time
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select

from bin.log import logger
from bin.get_task import *
from conf.settings import *


class Action(object):
    index_url = "https://mobile.eurowings.com/booking/Search.aspx?culture=en-GB"

    def __init__(self):
        """
        初始化浏览器
        """
        # 当前运行状态，如果页面动作出现错误之后将终止运行
        self.run_status = True
        try:
            self.driver = webdriver.Chrome()
            self.wait = WebDriverWait(self.driver, 20, 0.5)
            self.driver.get(self.index_url)

            time.sleep(3)
            self.driver.set_window_size(500, 700)
            logger.info("初始化webdriver对象")
        except TimeoutException:
            logger.error("初始化超时")
            self.run_status = False
        except Exception as e:
            logger.error("初始化webdriver对象失败" + str(e))
            self.run_status = False

    # 对input框输入内容
    def fill_input(self, content, xpath, single_input=False):
        """
        获取到xpath表达式，定位元素，输入内容
        :param args:
        :param kwargs:
        :return:
        """
        try:
            input_content = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    xpath
                ))
            )
            if input_content.is_enabled():
                # 一个一个字母输入
                input_content.clear()
                if single_input:
                    for item in content:
                        input_content.send_keys(item)
                        time.sleep(0.7)
                else:
                    input_content.send_keys(content)
            else:
                logger.debug(f"fill_input:{xpath}该元素不可操作")
                self.run_status = False
        except Exception as e:
            logger.error(f"定位{xpath}时，填写{content}时出错，错误信息：{str(e)}")
            self.run_status = False

    def click_btn(self, xpath):
        try:
            btn = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    xpath
                ))
            )
            if btn.is_enabled():
                btn.click()
                time.sleep(1)
            else:
                logger.debug(f"click_btn:{xpath}该元素不可操作")
                self.run_status = False
        except TimeoutException:
            logger.error(f"点击{xpath}超时")
            self.run_status = False
        except Exception as e:
            logger.error(f"定位{xpath}时，点击click时出错，错误信息：{str(e)}")
            self.run_status = False

    def select_date(self, div_num, day):
        """
        选择日期
        :param div_num:
        :param day:
        :return:
        """
        try:
            a = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    f'//*[@id="datepicker"]/div/div[{div_num}]'  # 2 是相对于当前的第几个月
                ))
            )
            # 如果day小于10，就要去掉前面的0
            day = str(int(day))
            a.find_element_by_link_text(f"{day}").click()

            logger.info("选择出发日期")
            time.sleep(1)

        except Exception as e:
            logger.error(f"选择出发日期时发生错误，错误信息：{str(e)}")
            self.run_status = False

    def get_text(self, xpath):
        try:
            h1 = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    xpath
                ))
            )
            return h1.text
        except Exception as e:
            logger.error(f"获取页面文本值出错，错误信息为{str(e)}")
            self.run_status = False

    def scroll_screen(self):
        scroll_screen_js = 'window.scroll(0, document.body.scrollHeight)'
        self.driver.execute_script(scroll_screen_js)


class Base(object):
    def calculation_age(self, passengers):
        """
        计算乘客的年龄
        passenger 是个包含每个乘客信息的列表
        :param passenger:
        :return:
        """
        # 成人默认是1
        self.adult = -1
        self.children = 0
        self.infants = 0

        current_year = datetime.now().year
        try:
            for passenger in passengers:
                passenger_birth = passenger["birthday"].split("-")[0]
                # 计算乘客年龄
                passenger_age = int(current_year) - int(passenger_birth)
                if passenger_age >= 12:
                    self.adult += 1
                elif 2 <= passenger_age < 12:
                    self.children += 1
                else:
                    self.infants += 1
        except Exception as e:
            logger.error(f"获取年龄出现错误，错误信息：{str(e)}")

    def calculation_luggage(self, baggageweight):
        """
        baggageweight:目标行李的重量
        根据行李的重量，分配行李的选择方式
        选择行李分为两个档次，一个是23KG，25块钱。一个是32KG，75块钱
        :param baggageweight:
        :return: 返回选择几个23KG和几个32KG
        """
        select_times = {"23": 0, "32": 0}
        # 100KG, 首先用目标重量小于32除23，如果结果小于1那么就选择一个23，

        if 32 < baggageweight <= 46:
            select_times["23"] = 2

        elif baggageweight <= 32 or 46 < baggageweight <= 142:
            s, y = divmod(baggageweight, 55)
            select_times["23"] = s
            select_times["32"] = s
            if y == 0:
                pass
            elif 0 < y <= 23:
                select_times["23"] += 1
            elif 23 < y <= 32:
                select_times["32"] += 1
            else:
                select_times["23"] += 1
                select_times["32"] += 1
        elif 142 < baggageweight <= 151:
            select_times["23"] = 1
            select_times["32"] = 4
        else:
            select_times["23"] = 0
            select_times["32"] = 5

        return select_times["23"], select_times["32"]


class FillFlightInfo(Action, Base):

    def __init__(self, task):
        """
        task: 获取到任务，字典格式
        :param task:
        """
        self.username = USERNAME
        self.password = PASSWORD

        # 从task中获取航班信息，进行初始化
        self.depAirport = task["depAirport"]
        self.arrAirport = task["arrAirport"]
        self.depFlightNumber = task["depFlightNumber"]
        # 出发日期
        self.depDate = task["depDate"]
        # 航班具体信息起飞时间和落地时间
        self.depTime = task["segmentVOList"][0]["depDate"][8:]
        self.arrTime = task["segmentVOList"][0]["arrDate"][8:]
        # 航班的价格信息
        self.targetPrice = task["targetPrice"]

        # 乘客信息
        self.passengerVOList = task["passengerVOList"]  # 列表包字典
        # 为了方便后续的添加行李，对乘客列表做一个排序
        self.passengerVOList.sort(key=lambda x: int(time.localtime().tm_year) - int(x["birthday"].split("-")[0]),
                                  reverse=True)
        self.passengerCount = task["passengerCount"]

        # 支付方式
        self.paymentMethod = task["payPaymentInfoVo"]["name"]
        # 卡号
        self.creditNum = task["payPaymentInfoVo"]["cardVO"]["cardNumber"]
        # 持卡人
        self.creditHold = task["payPaymentInfoVo"]["cardVO"]["lastName"] + "/" + \
                          task["payPaymentInfoVo"]["cardVO"]["firstName"]
        # 卡的过期时间
        self.creditExpires = task["payPaymentInfoVo"]["cardVO"]["cardExpired"].split("-")
        self.creditExpires.reverse()
        self.cvv = task["payPaymentInfoVo"]["cardVO"]["cvv"]

        # 初始化回填数据格式
        self.backdata = BACKFILLINFO
        # 回填乘客信息
        self.backdata["nameList"] = [item["name"] for item in self.passengerVOList]
        # 回填支付任务ID
        self.backdata["payTaskId"] = task["pnrVO"]["payTaskId"]
        # 回填联系地址
        self.backdata["linkEmail"] = task["contactVO"]["linkEmail"]
        self.backdata["linkEmailPassword"] = task["contactVO"]["linkEmailPassword"]
        self.backdata["linkPhone"] = task["contactVO"]["linkPhone"]
        # 回填支付卡的信息
        self.backdata["cardName"] = task["pnrVO"]["cardName"]
        self.backdata["cardNumber"] = task["pnrVO"]["cardNumber"]
        # 回填来源币种
        self.backdata["sourceCur"] = task["pnrVO"]["sourceCur"]
        self.backdata["targetCur"] = task["pnrVO"]["targetCur"]

        super(FillFlightInfo, self).__init__()

    def login(self):
        """
        点击登陆
        :param username:
        :param password:
        :return:
        """
        # 打开菜单
        # 获取菜单的定位
        menu_btn_xpath = '//*[@id="siteHeader"]/nav/span'
        self.click_btn(xpath=menu_btn_xpath)
        # 选择log in
        login_xpath = '//*[@id="login-icon"]'
        self.click_btn(login_xpath)
        # 输入内容
        self.fill_input(content=self.username, xpath='//*[@id="user"]')
        self.fill_input(content=self.password, xpath='//*[@id="password"]')

        # 点击login按钮
        self.click_btn(xpath='//*[@id="loginUser"]')

        logger.info("登陆完成")
        time.sleep(2)

    def select_flight_info(self):
        """
        选择航班信息出发地，目的地，出发时间，人数，先按照单程票购买
        :return:
        """
        logger.info("输入航班信息")
        # 点击One way，选择单程票
        oneway_btn = '//*[@id="siteContent"]/div[1]/div[3]/div[1]/label[2]'
        self.click_btn(oneway_btn)

        # 选择出发地
        depAir_xpath = '//*[@id="origin"]'
        self.click_btn(xpath=depAir_xpath)
        # 输入查询出发地
        depAir_input_xpath = '//*[@id="siteContent"]/div[3]/div[3]/div/input'
        self.fill_input(self.depAirport, xpath=depAir_input_xpath, single_input=True)
        time.sleep(2)
        # 选择查询到的第一个结果点击选择, 点击第一个会不准确
        result_xpath = '//*[@id="siteContent"]/div[3]/div[4]/ul[2]/li[@data-code="{}"]'.format(self.depAirport)
        self.click_btn(xpath=result_xpath)
        logger.debug("输入出发地")

        time.sleep(2)

        # 选择目的地
        arrAir_xpath = '//*[@id="destination"]'
        self.click_btn(xpath=arrAir_xpath)
        # 输入查询目的地
        arrAir_input_xpath = '//*[@id="siteContent"]/div[4]/div[3]/div/input'
        self.fill_input(self.arrAirport, xpath=arrAir_input_xpath, single_input=True)
        time.sleep(2)
        # 准确选择目的地
        result_xpath = '//*[@id="siteContent"]/div[4]/div[4]/ul/li[@data-code="{}"]'.format(self.arrAirport)
        self.click_btn(xpath=result_xpath)
        logger.debug("输入目的地")

        # 选择出发日期
        departure_xpath = '//*[@id="departuredate"]'
        self.click_btn(xpath=departure_xpath)
        # //*[@id="datepicker"]/div/div[1]/table/tbody/tr[5]/td[4]/a
        # 尝试点击日期
        year, month, day = self.depDate.split("-")
        # 获取当前月份
        current_month = datetime.now().month
        div_num = str(int(month) - int(current_month) + 1)
        # 选择出发日期
        self.select_date(div_num=div_num, day=day)

        # 点击选择乘客
        passenger_btn = '//*[@id="travellers"]'
        self.click_btn(xpath=passenger_btn)
        # 计算成人，儿童，婴儿的个数
        self.calculation_age(self.passengerVOList)
        # 点击+，选择人数
        adult_xpath = '//*[@id="siteContent"]/div[6]/div[2]/div/div[1]'
        children_xpath = '//*[@id="siteContent"]/div[6]/div[3]/div/div[1]'
        infants_xpath = '//*[@id="incInfant"]'
        all_li = {"adult": adult_xpath, "children": children_xpath, "infants": infants_xpath}
        for category in all_li:
            for item in range(getattr(self, category)):
                self.click_btn(xpath=all_li[category])

        # 点击确定
        done_btn = '//*[@id="setTravellerData"]'
        self.click_btn(xpath=done_btn)

        # 信息填写完毕，点击search按钮，查询航班信息
        search_btn = '//*[@id="SearchViewControlGroupFlightSelection_SearchViewFlightSearchControl_ButtonSubmit"]'
        self.click_btn(search_btn)

        logger.info("查询信息填写完毕")
        # 等待查询结果
        time.sleep(5)

    def result_handle(self):
        """
        获取所有的航班信息，匹配符合条件的一个
        判断出发地和目的地，还有航班好。出发地和目的地由于app的原因可能出现偏差，做个校验
        对价格做个校验，不能超过目标价格
        :return: bool
        """
        try:
            flight_dep = self.get_text(xpath='//*[@id="tripDeparture"]/div[2]/div[1]/div/p/span[1]')
            flight_arr = self.get_text(xpath='//*[@id="tripDeparture"]/div[2]/div[1]/div/p/span[3]')
            flight_dep = re.search(r"\((?P<flight_dep>.*?)\)", flight_dep).group("flight_dep")
            flight_arr = re.search(r"\((?P<flight_arr>.*?)\)", flight_arr).group("flight_arr")

            if self.depAirport != flight_dep or self.arrAirport != flight_arr:
                logger.info("出发地和目的地错误，购买失败")
                self.backdata["status"] = 402
                return False

            # 查询到的所有航班信息
            flight_info_list = self.driver.find_elements_by_xpath('//*[@id="tripDeparture"]/div[2]/div[3]/div')

            # 判断是否有航班
            try:
                tip = flight_info_list[0].find_element_by_xpath('./div/text()')
                if "Unfortunately there are no flights available for the route on the date selected" in tip:
                    logger.info("没有查询的航班信息")
                    return False
            except Exception as e:
                pass

            for flight in flight_info_list:
                # 获取航班号
                flight_num = flight.find_element_by_xpath('./a/div/div[3]/div[1]/div[1]').text.strip()
                # 获取航班的起飞时间和落地时间
                flight_depTime = flight.find_element_by_xpath('./a/div/div[2]/div[1]/div[1]').text
                flight_arrTime = flight.find_element_by_xpath('./a/div/div[2]/div[1]/div[3]').text
                if "PM" in flight_arrTime:
                    flight_arrTime = re.findall(r"(\d+)", flight_arrTime)
                    hour = int(flight_arrTime[0]) + 12
                    flight_arrTime[0] = str(hour)
                else:
                    flight_arrTime = re.findall(r"(\d+)", flight_arrTime)

                flight_depTime = "".join(re.findall(r"(\d+)", flight_depTime))
                flight_arrTime = "".join(flight_arrTime)
                # 与任务的航班信息
                if self.depFlightNumber == flight_num and self.depTime == flight_depTime and \
                        self.arrTime == flight_arrTime:
                    # 校验航班价格
                    # 获取航班价格，单价
                    flight_current_price = flight.find_element_by_xpath('./a//span[@class="value"]').text
                    self.flight_current_price = ".".join(re.findall(r"(\d+)", flight_current_price))
                    if float(self.targetPrice) >= float(self.flight_current_price):
                        # 任务价格大于当前航班价格
                        if flight.is_enabled():
                            flight.click()
                            time.sleep(2)
                            return True
                    else:
                        # 任务价格小于当前航班价格，不能购买, 修改回填任务的状态
                        logger.info("任务价格小于当前航班价格")
                        self.backdata["status"] = 403
                        return False
            else:
                logger.info("没有查询到对应的航班号，请重新输入查询")
                self.backdata["status"] = 402
                return False
        except Exception as e:
            logger.error(f"选择航班出现错误，错误信息：{str(e)}")
            return False

    def confirm_flight_info(self):
        try:
            # 点击base
            base_div_js = """document.querySelector('#tripDeparture > div.tripJourneys > div.tripJourneyDate > div > div.tariffList.open > div.fare-wrapper.tripFare.BASIC').click()"""
            self.driver.execute_script(base_div_js)
            # 点击进行下一步
            time.sleep(2)
            continue_btn = '//*[@id="SelectViewControlGroupFlightSelection_ButtonSubmit"]'
            self.click_btn(xpath=continue_btn)

            logger.info("确认航班信息")
        except Exception as e:
            logger.error(f"确认航班信息出错，错误信息是：{str(e)}")

    def fill_passenger_info(self):
        """
        注意：如果乘客中有儿童，第一个成人乘客需要调协birthday信息，如果没有儿童或者婴儿，不需要填写乘客信息。
        儿童和婴儿都需要填写birthday信息
        :return:
        """
        # 输入日期 year： //*[@id="siteContent"]/div[6]/fieldset/div/div[2]/input
        # 输入日期 month: //*[@id="siteContent"]/div[6]/fieldset/div/div[3]/input

        firstname_xpath = '//*[@id="siteContent"]/div[{}]/div[2]/input'
        lastname_xpath = '//*[@id="siteContent"]/div[{}]/div[4]/input'
        # 输入出生日期的xpath //*[@id="siteContent"]/div[4]/fieldset/div/div[2]/input
        birth_xpath = '//*[@id="siteContent"]/div[{}]/fieldset/div/div[{}]/input'  # 第一个放的是哪个乘客，第二个是年月日
        # gender xpath
        gender_xpath = '//*[@id="siteContent"]/div[{}]/div[1]/label[{}]'
        # 选择乘客性别
        for index, passenger in enumerate(self.passengerVOList):
            gender = passenger.get("sex")
            firstname, lastname = passenger.get("name").split("/")
            if gender == "F":
                self.click_btn(gender_xpath.format(index + 4, 1))
            else:
                self.click_btn(gender_xpath.format(index + 4, 2))
            self.fill_input(content=firstname, xpath=firstname_xpath.format(index + 4))
            self.fill_input(content=lastname, xpath=lastname_xpath.format(index + 4))

            time.sleep(1)
            # 填写乘客出生信息
            if (self.children != 0 or self.infants != 0 and index == 0) or \
                    (int(time.localtime().tm_year) - int(passenger["birthday"].split("-")[0]) < 12):
                # 携带儿童或者婴儿的第一个乘客 or
                # 年龄小于12岁的儿童或者婴儿
                date_li = passenger["birthday"].split("-")
                date_li.reverse()
                for item, d in enumerate(date_li):
                    self.fill_input(content=d, xpath=birth_xpath.format(index + 4, item + 2))

    def fill_invoice_data(self):
        address = "beijingshi fengtaiqu dahongmen tianshiyuan"
        address_xpath = '//*[@id="ContactViewControlGroupContactInput_ContactViewContactInputControl_AddressLine1"]'
        post_card = "100000"
        post_card_xpath = '//*[@id="ContactViewControlGroupContactInput_ContactViewContactInputControl_PostalCode"]'
        city = 'beijing'
        city_xpath = '//*[@id="ContactViewControlGroupContactInput_ContactViewContactInputControl_City"]'
        email = "12345678909@163.com"
        emali_xpath = '//*[@id="ContactViewControlGroupContactInput_ContactViewContactInputControl_Email"]'

        self.fill_input(content=address, xpath=address_xpath)
        self.fill_input(content=post_card, xpath=post_card_xpath)
        self.fill_input(content=city, xpath=city_xpath)
        self.fill_input(content=email, xpath=emali_xpath)

    def select_payment_method(self):
        """
        选择支付方式
        在这里修改支付状态
        :return:
        """
        credit_js = """document.querySelector('#paymentInputs > div.layerDefault > ul > li:nth-child(4) > a').click()"""
        self.driver.execute_script(credit_js)
        time.sleep(3)
        target_pyment_method = self.paymentMethod
        if target_pyment_method == "虚拟卡":
            mastercard_js = """document.querySelector('#creditCard > div > div.openBottomMask.trigger-toogle.link').click()"""
            self.driver.execute_script(mastercard_js)
            time.sleep(1)
            mastercard_xpath = '//*[@id="siteContent"]/div[7]/div[7]/ul/li[4]'
            self.click_btn(xpath=mastercard_xpath)
            # 输入卡号
            credit_num_xpath = \
                '//*[@id="PaymentViewControlGroupPaymentInput_PaymentViewPaymentInputControl_AccountNumber"]'
            self.fill_input(content=self.creditNum, xpath=credit_num_xpath)
            credit_hold_xpath = \
                '//*[@id="PaymentViewControlGroupPaymentInput_PaymentViewPaymentInputControl_AccountHolder"]'
            self.fill_input(content=self.creditHold, xpath=credit_hold_xpath)
            credit_expire_m = '//*[@id="fakeMonth"]'
            credit_expire_y = '//*[@id="fakeYear"]'
            credit_expire_cvv_js = """document.getElementsByName('PaymentViewControlGroupPaymentInput$PaymentViewPaymentInputControl$VerificationCode')[1].value = {}"""
            self.fill_input(content=self.creditExpires[0], xpath=credit_expire_m)
            self.fill_input(content=self.creditExpires[1], xpath=credit_expire_y)

            # 填写cvv
            self.driver.execute_script(credit_expire_cvv_js.format(self.cvv))

            # 点击to booking overview
            to_book_xpath = '//*[@id="paymentOverview"]/button[1]'
            self.click_btn(to_book_xpath)

            time.sleep(2)
            error_msg_xpath = '//*[@id="notificationInvalidPayment"]/div[2]/div/div/p'
            error_text = self.get_text(xpath=error_msg_xpath)
            if "Your payment details were not accepted. Please check you entered the correct information" in error_text:
                logger.info("购买失败")
                return False
            # 判断支付成功， 返回True，支付成功的标志就是获取到pnr号。
            # 获取单号
            # 。。。。。。

        elif target_pyment_method == "":
            return False
        else:
            # 不进行处理
            return False

    def select_luggage(self):
        """
        根据乘客选择行李
        :return:
        """
        current_year = datetime.now().year

        # 点击选择行李的xpath
        booking_luggage_xpath = '//*[@id="siteContent"]/a[1]'
        self.click_btn(xpath=booking_luggage_xpath)
        # 等待进入选择行李界面
        time.sleep(2)
        add_luggage_xpath = '//*[@id="siteContent"]/div[1]/a[{}]'
        add_num = 1
        # 计算add luggage的位置数
        for passenger in self.passengerVOList:
            if passenger.get("baggageWeight") and int(passenger["baggageWeight"]) > 0:
                times_23, times_32 = self.calculation_luggage(int(passenger["baggageWeight"]))
                # 判断是成人还是儿童还是婴儿
                passenger_birth = passenger["birthday"].split("-")[0]
                # 计算乘客年龄
                passenger_age = int(current_year) - int(passenger_birth)
                if passenger_age >= 12:
                    print(f"23件数：{times_23}, 32件数：{times_32}")
                    self.select_luggage_click(
                        add_num,
                        times_23,
                        times_32,
                        add_luggage_xpath.format(add_num)
                    )

                    add_num += 1
                elif 2 <= passenger_age < 12:
                    tmp_add_num = add_num
                    print(f"23件数：{times_23}, 32件数：{times_32}")
                    self.select_luggage_click(
                        tmp_add_num,
                        times_23,
                        times_32,
                        add_luggage_xpath.format(tmp_add_num)
                    )
                    add_num += 1
                else:
                    print(f"23件数：{times_23}, 32件数：{times_32}")
                    tmp_add_num = add_num
                    self.select_luggage_click(
                        tmp_add_num,
                        times_23,
                        times_32,
                        add_luggage_xpath.format(tmp_add_num)
                    )
                    add_num += 1
            else:
                add_num += 1
        else:
            apply_btn_xpath = '//*[@id="BaggageViewControlGroupServices_ButtonSubmit"]'
            self.click_btn(xpath=apply_btn_xpath)

    def select_luggage_click(self, passenger_num, times_23, times_32, xpath):
        """

        :param times_23: xpath: //*[@id="BAGGROUP_FLIGHT_0_PAX_0_BAG_1"]/div[1]/label[1]
        :param times_32: xpath: //*[@id="BAGGROUP_FLIGHT_0_PAX_0_BAG_1"]/div[1]/label[2]
        :param xpath: add luggage 按钮
        :return:
        """
        add_item_luggage_xpath = '//*[@id="BAGGROUP_FLIGHT_0_PAX_{}_BAG_{}"]/div[2]/a[2]'
        # 选择23，还是32
        up_to_kg_xpath = '//*[@id="BAGGROUP_FLIGHT_0_PAX_{}_BAG_{}"]/div[1]/label[{}]'

        passenger_num -= 1
        self.click_btn(xpath=xpath)
        time.sleep(1)
        if times_23 == 0 and times_32 == 1:
            self.click_btn(xpath=up_to_kg_xpath.format(passenger_num, 1, 2))
        elif times_23 == 1 and times_32 == 0:
            self.click_btn(xpath=up_to_kg_xpath.format(passenger_num, 1, 1))
        # elif times_32 > 1 and times_23 != 0:
        elif times_32 >= times_23:
            tmp_times_23 = times_23
            click_num = times_23 + times_32
            click_count = click_num + 1
            flag = True
            for item in range(times_32):

                # 只点击一次
                if flag:
                    self.click_btn(up_to_kg_xpath.format(passenger_num, item + 1, 2))
                    flag = False
                    time.sleep(1)
                if tmp_times_23 > 0:
                    self.click_btn(add_item_luggage_xpath.format(passenger_num, click_count - click_num))
                    click_num -= 1
                    time.sleep(1)
                    tmp_times_23 -= 1
                    # 滑动屏幕
                    self.scroll_screen()
                if item != times_32 - 1:
                    self.click_btn(add_item_luggage_xpath.format(passenger_num, click_count - click_num))
                    time.sleep(0.5)
                    # 滑动屏幕
                    self.scroll_screen()
                    self.click_btn(up_to_kg_xpath.format(passenger_num, item + 2, 2))
                    click_num -= 1

        elif times_23 > times_32:
            tmp_times_32 = times_32
            click_num = times_23 + times_32
            click_count = click_num + 1
            flag = True
            for item in range(times_23):

                # 只点击一次
                if flag:
                    self.click_btn(up_to_kg_xpath.format(passenger_num, item + 1, 1))
                    flag = False
                    time.sleep(1)
                if tmp_times_32 > 0:
                    self.click_btn(add_item_luggage_xpath.format(passenger_num, click_count - click_num))
                    click_num -= 1
                    time.sleep(1)
                    self.click_btn(up_to_kg_xpath.format(passenger_num, item + 2, 2))
                    tmp_times_32 -= 1
                    # 滑动屏幕
                    self.scroll_screen()
                if item != times_23 - 1:
                    self.click_btn(add_item_luggage_xpath.format(passenger_num, click_count - click_num))
                    click_num -= 1

        # 点击确认
        confirm_xpath = '//*[@id="siteContent"]/div[{}]/div[3]/button[1]'.format(passenger_num + 2)
        self.click_btn(xpath=confirm_xpath)

    def get_bagges_price(self):
        # 获取总价格
        # 打开价钱明细的窗口
        # 获取总价格
        total_price_xpath = '//*[@id="priceBox"]/div[1]/span[3]/span'
        total_price = self.get_text(total_price_xpath).strip().replace(",", "")

        amount_due_xpath = '//*[@id="priceBox"]/div[1]/span[2]'
        self.click_btn(xpath=amount_due_xpath)
        time.sleep(1)
        # //*[@id="priceBox"]/div[2]/table/tbody/tr[3]/td[2]
        luggage_fees_xpath = '//*[@id="priceBox"]/div[2]/table/tbody/tr[3]/td[2]'
        luggage_fees = self.get_text(xpath=luggage_fees_xpath)
        luggage_fees = "".join(re.findall(r"([\d.]+)", luggage_fees))
        # 判断运行状态是否健康
        # 回填行李行李价格
        self.backdata["baggagePrice"] = luggage_fees
        # 回填总价格（不包含行李价格）
        self.backdata["price"] = float(total_price) - float(luggage_fees)

    def __call__(self, *args, **kwargs):
        # 关闭cookie弹窗
        # 获取ok_btn: //*[@id="cookieAccept"]
        ok_btn_xpath = '//*[@id="cookieAccept"]'
        self.click_btn(xpath=ok_btn_xpath)
        # 登陆操作, 不需要登陆
        # self.login()

        # 选择航班信息
        self.select_flight_info()

        # 查询结果的处理
        pur_bool = self.result_handle()
        if pur_bool:
            # 航班号匹配正确点击购买
            self.confirm_flight_info()
            time.sleep(2)
            # 之后有两个选择，一个是Booking luggage
            # 判断是否需要选择行李
            luggage_bool = False
            for item in self.passengerVOList:
                if int(item["baggageWeight"]) > 0:
                    luggage_bool = True
                    break
            if luggage_bool:
                self.select_luggage()
            # 填写乘客信息
            # 点击去往乘客信息
            to_passenger_data_xpath = '//*[@id="ServicesOverviewViewControlGroup_ButtonSubmit"]'
            self.click_btn(xpath=to_passenger_data_xpath)
            time.sleep(2)

            # 判断运行状态，是否可以继续运行
            if self.run_status:
                # 填写乘客信息
                self.fill_passenger_info()
                to_invoice_xpath = '//*[@id="PassengerViewControlGroupPassengerInput_ButtonSubmit"]'
                self.click_btn(xpath=to_invoice_xpath)
            else:
                self.backdata["status"] = 401
                return self.backdata

            # 判断运行状态，是否可以继续运行
            if self.run_status:
                # 填写发票信息
                self.fill_invoice_data()
                # 点击to payment method
                to_payment_method_xpath = '//*[@id="ContactViewControlGroupContactInput_ButtonSubmit"]'
                self.click_btn(xpath=to_payment_method_xpath)
                time.sleep(2)
            else:
                self.backdata["status"] = 401
                return self.backdata

            if self.run_status:
                # 计算行李价格
                self.get_bagges_price()
                # 选择支付方式
                self.select_payment_method()

                return self.backdata

        else:
            # 购买失败，没有获取到对应的航班
            # 修改回填状态
            logger.info("支付失败")
            return self.backdata

    # def __del__(self):
    #     self.driver.close()


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
    backdata = fill_flight_info()  # 返回回填的数据
    print(backdata)
