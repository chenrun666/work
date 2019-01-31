import time
import json
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select

from result import bookStatus
from line_data import *

payFail = bookStatus["PayFail"]

logger_crawl = logging.getLogger('./log/join_crawl_imgs.log')
logger_crawl.setLevel(logging.INFO)
# 建立一个filehandler来把日志记录在文件里，级别为debug以上
fh = logging.FileHandler("join_crawl_imgs.log", encoding='utf-8')
fh.setLevel(logging.INFO)
# 建立一个streamhandler来把日志打在CMD窗口上，级别为error以上
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# 设置日志格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# 将相应的handler添加在logger对象中
logger_crawl.addHandler(ch)
logger_crawl.addHandler(fh)


# 处理没有小孩子的订单
def get_indexs(tasks, adult, teen, chirld, results, passengerCount):
    # 出发地和目的地，起飞时间
    orgin = tasks["depAirport"]
    Destination = tasks["arrAirport"]
    date = tasks["depDate"]

    try:
        # 本机驱动路径
        driver = webdriver.Chrome(
            # executable_path="C:\\Users\\MACHENIKE\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\chromedriver.exe"
        )
        # 服务器驱动路径
        # driver = webdriver.Chrome(
        #     executable_path="C:\\Users\\Administrator\\Desktop\\result\\chromedriver.exe"
        # )

        wait = WebDriverWait(driver, 20, 0.5)
        index_url = 'https://www.ryanair.com/us/en/booking/home/{}/{}/{}//{}/{}/{}/0'.format(orgin, Destination, date,
                                                                                             adult, teen, chirld)
        print(index_url)
        driver.get(index_url)
        time.sleep(5)
        driver.maximize_window()
    except Exception as e:
        status = payFail
        errorMsg = '在加载首页时候出现异常'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    flightNumber = tasks["depFlightNumber"]
    flights_list = []
    try:
        # 获取当前查询日期，有多少个航班
        for f in range(10):
            # 获取航班号
            flight = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@class='flights-table']/div/div[{}]/flights-table-header/div/div/div[2]/div/div/div[3]".format(
                                                    f + 1)))
            )
            flights_list.append(flight.text.replace(' ', ''))

        # author:chenrun; 修改建议#########################
        # flight_num_list = wait.until(
        #     EC.presence_of_all_elements_located((By.XPATH,
        #                                          "//*[@class='flights-table']/div/div[1]/"
        #                                          "flights-table-header/div/div/div/div/div/div[3]"))
        # )
        # for flight in flight_num_list:
        #     flights_list.append(flight.text.replace(' ', ''))
        ######################################################

    except TimeoutException:
        pass

    time.sleep(1)

    try:
        # 根据任务航班号匹配对应页面的航班号
        localtion_index = flights_list.index(flightNumber) + 1
        print(localtion_index)
    except Exception as e:
        status = payFail
        errorMsg = '网络延迟导致没查到当前出票航班'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 找到对应航班对应的价格按钮
    try:
        low_price = driver.find_element_by_xpath(
            "//*[@class='flights-table']/div/div[{}]/flights-table-header/div/div[2]".format(localtion_index))
        low_price.click()
        time.sleep(3)

        many_chirld = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="flights-table-fares"]/div/div[1]')))
        many_chirld.click()
        time.sleep(7)
    except Exception as e:
        status = payFail
        errorMsg = '查询航班对应的按钮的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        # 获取总价 total cost
        prices = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="booking-selection"]/article/div[2]/section/div/trips-breakdown/div/div/div[2]'
        )))
        ticket_price = float(prices.text.split()[1].replace(',', ''))
        results["nameList"] = tasks["pnrVO"]["nameList"]  # 获取任务里的客户列表
        print('这是票总价', ticket_price)
        time.sleep(2)

        # 获取到continue，点击continue继续
        continues = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="continue"]'))
        )
        continues.click()
        time.sleep(3)

    except Exception as e:
        status = payFail
        errorMsg = '价格页面时候continue出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 改版后，需要点击小黑包，每个乘客单独选
    try:
        black_bag = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@class="priority-boarding-view"]/div[2]/div[2]/div/priority-cabin-bag-card[1]/div/div[3]'
        )))
        black_bag.click()

        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '改版后点击小黑包错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 点击小黑包之后的弹出框，选择yes，点击继续
    try:
        same_bags = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@class="same-for-all-form"]/div[4]/button[2]'
        )))
        same_bags.click()
        time.sleep(5)
    except Exception as e:
        print(e)
        # print('一个人的时候出现异常')
        pass

    try:
        continues = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@class="priority-boarding-view"]/div[2]/div[3]/button'
        )))
        continues.click()
        time.sleep(3)

        # 选择作为，如果有小孩（child）必须座位必须挨着，否则就是随机选择
        random_seat = wait.until(EC.presence_of_element_located((
            # By.XPATH,'//*[@id="dialog-body-slot"]//following-sibling::div[2]/dialog-footer-info/div/div[3]/div[3]/div[3]/div[2]/button[2]'
            By.XPATH,
            '//*[@id="dialog-body-slot"]//following-sibling::div[2]/dialog-footer-info/div/div[3]/div[2]/div[3]/div[2]/button[2]'
        )))
        random_seat.click()
        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '改版后点击continue错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 循环   选行李
    try:
        weight_list = []
        # 客户列表
        passengerVOList = tasks["passengerVOList"]
        for weight in passengerVOList:
            # 客人拿包的重量
            baggageWeight = weight["baggageWeight"]
            weight_list.append(baggageWeight)
        # weight_list = [0]
        print(weight_list)
        bag_price = 0
        # 计算总重量的价钱
        # 选择增加行李代码有问题
        # if sum(weight_list) != 0:
        #     if adult != 0 and teen != 0:
        #         add_bag_click = wait.until(
        #             # EC.presence_of_element_located((By.XPATH,'//*[@id="RECOMMENDED"]/section/div[2]/extras-card[3]/div/div'))
        #             # 点击换座位
        #             EC.presence_of_element_located(
        #                 (By.XPATH, '//*[@class="extras-panel__sections"]/extras-section/section/div[2]/extras-card[1]'))
        #         )
        #         add_bag_click.click()
        #     elif adult != 0 and teen == 0:
        #         add_bag_click = wait.until(
        #             # EC.presence_of_element_located((By.XPATH,'//*[@id="RECOMMENDED"]/section/div[2]/extras-card[3]/div/div'))
        #             # 点击加包重量
        #             EC.presence_of_element_located(
        #                 (By.XPATH, '//*[@class="extras-panel__sections"]/extras-section/section/div[2]/extras-card[2]'))
        #         )
        #         add_bag_click.click()
        #     else:
        #         # 如果是tee单独一个人坐飞机，漏判断
        #         pass

        # 计算行李重量
        if sum(weight_list) != 0:
            # 点击增加行李包裹
            add_bag_click = wait.until(
                # 点击加包重量
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="extras-panel__sections"]/extras-section/section/div[2]/extras-card[2]'))
            )
            add_bag_click.click()
            time.sleep(3)
            for w in range(len(weight_list)):
                if weight_list[w] == 0:
                    pass
                elif 0 <= weight_list[w] <= 20:  # 选择一份
                    first_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[1]/div/div[{}]'.format(
                                                            w + 1, w + 1)))
                    )
                    first_bag.click()
                elif 20 < weight_list[w] <= 40:
                    first_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[1]/div/div[{}]'.format(
                                                            w + 1, 1)))
                    )
                    sec_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[2]/div/div[{}]'.format(
                                                            w + 1, 1)))
                    )
                    first_bag.click()
                    time.sleep(1)
                    sec_bag.click()
                else:
                    first_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[1]/div/div[{}]'.format(
                                                            w + 1, 1)))
                    )
                    sec_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[2]/div/div[{}]'.format(
                                                            w + 1, 1)))
                    )
                    third_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[3]/div/div[{}]'.format(
                                                            w + 1, 1)))
                    )
                    first_bag.click()
                    time.sleep(1)
                    sec_bag.click()
                    time.sleep(1)
                    third_bag.click()
            bag_prices = wait.until(EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="dialog-body-slot"]/following-sibling::div[1]/dialog-footer/dialog-overlay-footer/div/div[3]/div/span[2]'
            )))
            bag_price = float(bag_prices.text.split()[1].replace(',', ''))

            confirms = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="dialog-body-slot"]/following-sibling::div[1]/dialog-footer/dialog-overlay-footer/div/div[3]/disabled-tooltip/span/ng-transclude/tooltip-target/button-spinner/button'))
            )
            confirms.click()
            time.sleep(5)
    except Exception as e:
        status = payFail
        errorMsg = '点击行李按钮时候出现异常'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results
    results["baggagePrice"] = bag_price
    # total_price = float(price) + float(bag_price)
    print('这是行李价格', bag_price)

    # 点击check_out
    try:
        check_out = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="booking-selection"]/article/div[2]/section/div[2]/button'
            ))
        )
        check_out.click()
        time.sleep(5)
    except Exception as e:
        status = payFail
        errorMsg = '点击check_out的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 点击nothanks
    try:
        nothanks = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="popup-msg"]/div[2]/div[2]/div[4]/button[2]')))
        nothanks.click()
        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '点击nothanks的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        pass

    # 跳出登陆页面，点击Log in 按钮
    try:
        print("已经要输入账号密码了")
        login_button = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@ui-sref="login"]'
        )))
        login_button.click()
        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '点击登录按钮时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        usernames = tasks["pnrVO"]["accountUsername"]
        passwords = tasks["pnrVO"]["accountPassword"]
        username = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@type="email"]'
            ))
        )
        password = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@type="password"]'
            ))
        )
        username.send_keys(usernames)
        time.sleep(1)
        password.send_keys(passwords)
        time.sleep(1)
        login_button = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@type="submit"]'
            ))
        )
        login_button.click()
        time.sleep(5)
    except Exception as e:
        status = payFail
        errorMsg = '输入账号密码的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 进入最后一页输入乘客信息以及卡号信息
    passge = tasks["passengerVOList"]
    for i in range(len(passge)):
        try:
            gender = passge[i]["sex"]
            selects = driver.find_element_by_xpath(
                "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[1]/div/select".format(i + 1))
            time.sleep(2)
            if gender == 'M':
                Select(selects).select_by_value('string:MR')
            else:
                Select(selects).select_by_value('string:MS')

        except Exception as e:
            status = payFail
            errorMsg = '选择乘客性别时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results

        try:
            first_names = passge[i]["name"].split('/')[0]  # 姓
            last_names = passge[i]["name"].split('/')[1]  # 名

            first_name = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[2]/input".format(
                                                    i + 1)))
            )  # 名字输入框
            first_name.send_keys(last_names)
            time.sleep(1)
            last_name = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[3]/input".format(
                                                    i + 1)))
            )  # 姓输入框
            last_name.send_keys(first_names)
            time.sleep(3)
        except Exception as e:
            status = payFail
            errorMsg = '输入乘客姓名时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results

    # 输入手机号
    try:
        phone_numm_select = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="checkout"]/div/form/div[1]/div[3]/div[2]/contact-details-form/div/div[1]/div[3]/phone-number/div[1]/div/select/optgroup[2]/option[37]'
            ))
        )
        phone_numm_select.click()
        time.sleep(2)
        phone_numm_input = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="checkout"]/div/form/div[1]/div[3]/div[2]/contact-details-form/div/div[1]/div[3]/phone-number/div[2]/input'
            ))
        )
        phone_num = tasks["pnrVO"]["linkPhone"]
        phone_numm_input.send_keys(phone_num)
    except Exception as e:
        status = payFail
        errorMsg = '选择手机号码所属地或输入手机号的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 输入卡号
    card_num = tasks["payPaymentInfoVo"]["cardVO"]["cardNumber"]
    try:
        card_num_inpuit = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@name="cardNumber"]'
            ))
        )
        card_num_inpuit.send_keys(card_num)
        time.sleep(3)
    except Exception as e:
        try:
            use_another_card = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@for="radio-single-new"]'
            )))
            use_another_card.click()
            time.sleep(2)
            card_number = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@name="cardNumber"]'
            )))
            card_number.send_keys(card_num)
            time.sleep(3)
        except Exception as e:
            print("选择使用另外一张卡时候出错")
            status = payFail
            errorMsg = '输入卡号的时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results

    # 判断卡是否有效
    try:
        invalid = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@class="card-method"]/div[1]/ul/li/span'
        )))
        if invalid.text == 'Card number is invalid':
            status = payFail
            errorMsg = '卡号无效'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results
    except Exception as e:
        pass
    time.sleep(2)
    try:
        cvv_num = tasks["payPaymentInfoVo"]["cardVO"]["cvv"]
        cardholder = tasks["payPaymentInfoVo"]["cardVO"]["firstName"]

        cardexpired = tasks["payPaymentInfoVo"]["cardVO"]["cardExpired"]
        y = cardexpired.split('-')[0]
        m = int(cardexpired.split('-')[1])
        months = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@name="expiryMonth"]'
            ))
        )
        Select(months).select_by_value("number:{}".format(m))
        time.sleep(1)
        years = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@name="expiryYear"]'
        )))
        Select(years).select_by_value('number:{}'.format(y))
        time.sleep(1)
        cvv = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@name="securityCode"]'
            )))
        cvv.send_keys(cvv_num)
        time.sleep(1)
        card_name_input = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@name="cardHolderName"]'
            )))
        card_name_input.send_keys(cardholder)
        time.sleep(1)
    except Exception as e:
        status = payFail
        errorMsg = '选择卡的有效日期或者输入cvv失败'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        address1 = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="billingAddressAddressLine1"]'))
        )
        address1.send_keys('丰台区大红门天世元')
        time.sleep(1)

        address2 = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="billingAddressAddressLine2"]'))
        )
        address2.send_keys('丰台区大红门天世元')
        time.sleep(1)

        city = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="billingAddressCity"]'))
        )
        city.send_keys('BEIJING')
        time.sleep(1)

        zip_code = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="billingAddressPostcode"]'))
        )
        zip_code.send_keys('100000')
        time.sleep(1)

        country = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="billingAddressCountry"]/optgroup[2]/option[37]'))
        )
        country.click()
        time.sleep(1)
    except Exception as e:
        status = payFail
        errorMsg = '输入地址或者选择国家城市的时候出现异常'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        gou_js = "document.getElementsByName('acceptPolicy')[0].click()"
        driver.execute_script(gou_js)
        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '点击同意小框时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 获取总价格，包含行李和票价以及手续费
    total_ticket_price = wait.until(EC.presence_of_element_located((
        By.XPATH, '//*[@class="overall-total"]/span[2]'
    )))
    total_ticket_price = float(total_ticket_price.text.split()[1].replace(',', ''))
    print("这是总价格，包含行李和手续费", total_ticket_price)
    include_tax_price = (total_ticket_price * 100) - (bag_price * 100)
    results["price"] = include_tax_price / 100
    print('这是减去行李之后的价格，包含手续费和票价', include_tax_price / 100)

    target_price = (int(tasks["targetPrice"]) + 1) * passengerCount
    print(json.dumps(results))
    if ticket_price <= target_price:
        print("对比价格后可以出票")
        print(json.dumps(results))
        try:
            pay_button = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@class="cta"]/button'
            )))
            pay_button.click()
            time.sleep(5)
            try:
                error = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@class="body"]/payment-details-form/div/div[2]/prompt/div[2]'
                )))
                if error.text != []:
                    errorMsg = 'As your payment was not authorised we could not complete your reservation. Please ensure that the information was correct or use a new payment to try again'
                    results["status"] = payFail
                    results["errorMessage"] = errorMsg
                    logger_crawl.error('{}'.format(errorMsg))
                    return results
                else:
                    time.sleep(30)
                    # 点击支付按钮后，获取票号
                    try:
                        pnr = wait.until(EC.presence_of_element_located((
                            By.XPATH, "//*[@class='booking-details__summary']/div[3]/div[2]/span"
                        )))
                        pnr = pnr.text
                        print("这是票号，{}".format(pnr))
                        logger_crawl.info("这是票号" + pnr)
                        if pnr != "":
                            errorMsg = '支付成功'
                            results["pnr"] = pnr
                            results["status"] = bookStatus["PaySuccess"]
                            results["errorMessage"] = errorMsg
                            logger_crawl.error('{},{}'.format(errorMsg, results))
                            print(json.dumps(results))
                            input("输入点东西")
                            return results
                        else:
                            errorMsg = '点击支付，但是未获取到票号'
                            results["pnr"] = pnr
                            results["status"] = bookStatus["PayFailAfterSubmitCard"]
                            results["errorMessage"] = errorMsg
                            logger_crawl.error('{},{}'.format(errorMsg, results))
                            print(json.dumps(results))
                            input("输入点东西")
                            return results
                    except Exception as e:
                        errorMsg = '获取票号时候时候出现错误'
                        results["status"] = bookStatus["PayFailAfterSubmitCard"]
                        results["errorMessage"] = errorMsg
                        logger_crawl.error('{},{}'.format(errorMsg, e))
                        return results
            except Exception as e:
                logger_crawl.error('判断是否出现卡未授权')
                # 修改状态
                pass

        except Exception as e:
            status = payFail
            errorMsg = '点击支付按钮时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results
    else:
        status = payFail  # 401, 支付失败
        errorMsg = '出票时候，票总价大于传回来的价格'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{}'.format(errorMsg))
        return results
