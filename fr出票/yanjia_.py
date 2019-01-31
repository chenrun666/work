from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import logging, json, requests
from result import bookStatus, result
from line_data import *
from fr_ticket import *

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


# 获取任务
def get_task():
    taskheaders = {'Content-Type': 'application/json'}
    data = {
        "clientType": "FR_PAY_CLIENT",
        "machineCode": "frbendi"
    }
    taskJson = requests.post("http://47.92.119.88:18002/getBookingPayTask",
                             data=json.dumps(data), headers=taskheaders)
    return taskJson.text


# 得到token,从line_Data.py文件的结果里拿到data
def get_flight_data(data, flight_number, datas, results):
    numbers = flight_number[2:]
    routings = data["routings"]
    for data in routings:
        number = data["fromSegments"][0]["flightKey"]
        if numbers not in number:
            pass
        else:
            fareKey = data["fromSegments"][0]["cabin"]
            flightKey = data["fromSegments"][0]["flightKey"]
            data = {"INF": 0, "CHD": 1, "ADT": 1, "TEEN": 0, "DISC": "",
                    "flights": [{"flightKey": flightKey,
                                 "fareKey": fareKey, "promoDiscount": False, "FareOption": ""}],
                    "promoCode": ""}

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
                'Content-Type': 'application/json'
            }

            # 返回X-Session-Token
            urls = 'https://desktopapps.ryanair.com/v4/en-us/Flight'
            session_token = requests.post(urls, data=json.dumps(data), headers=headers)
            try:
                token = session_token.headers["X-Session-Token"]
                return token
            except Exception as e:
                status = payFail
                errorMsg = '没有获取到token'
                results["status"] = status
                results["errorMessage"] = errorMsg
                logger_crawl.error('{},{}'.format(errorMsg, e))
                return results


# 获取所有可以点击的座位
def get_seat(token, datas, results):
    # 获取已经被选过的座位
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'Content-Type': 'application/json',
        'x-session-token': token
    }
    uurl = 'https://desktopapps.ryanair.com/v4/en-us/seat'
    seats = requests.get(uurl, headers=headers)
    print(seats.text)
    equipmentModel = json.loads(seats.text)[0]["equipmentModel"]
    unavailableSeats = json.loads(seats.text)[0]["unavailableSeats"]
    # 获取当前航班所有的座位信息
    all_seats_url = 'https://desktopapps.ryanair.com/v4/en-us/res/seatmap?aircraftModel={}&cache=true'.format(
        equipmentModel)
    all_seats = requests.get(all_seats_url)
    seatRows = json.loads(all_seats.text)[0]["seatRows"]

    # 获取所有可点的座位信息
    try:
        seat_list = []
        for seatRow in seatRows[16:]:
            for seat in seatRow:
                if len(seat["designator"]) < 4:
                    seat_list.append(seat["designator"])
                else:
                    pass
        # 剔除不可用的座位
        for s in unavailableSeats:
            if int(s[:2]) < 18:
                pass
            else:
                if s in seat_list:
                    seat_list.remove(s)
        for r in seat_list:
            if len(r) > 4:
                seat_list.remove(r)
        return seat_list
    except Exception as e:
        status = payFail
        errorMsg = '没有获取到可点击的座位'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results


# 回传数据
def send_data(data):
    print(data)
    taskheaders = {'Content-Type': 'application/json'}
    url = 'http://47.92.119.88:18002/bookingPayTaskResult'
    response = requests.post(url, data=json.dumps(data), headers=taskheaders)
    if json.loads(response.text)["status"] == 'Y':
        print('回填任务成功')
        with open('./log/success_data.txt', 'a+')as f:
            f.write(json.dumps(data) + '\n')
    else:
        print('回传任务失败')
        with open('./log/error_data.txt', 'a+')as f:
            f.write(json.dumps(data) + '\n')


def get_index(orgin, Destination, date, adult, teen, chirld, can_click_seat, tasks, results, passengerCount):
    try:
        # 本机驱动路径
        driver = webdriver.Chrome(
            # executable_path="C:\\Users\\MACHENIKE\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\chromedriver.exe"
        )
        # 服务器驱动路径
        # driver = webdriver.Chrome(
        #     executable_path="C:\\Users\\Administrator\\Desktop\\result\\chromedriver.exe"
        # )
        wait = WebDriverWait(driver, 15, 0.5)
        index_url = 'https://www.ryanair.com/us/en/booking/home/{}/{}/{}//{}/{}/{}/0'.format(orgin, Destination, date,
                                                                                             adult, teen, chirld)
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
            flight = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@class='flights-table']/div/div[{}]/flights-table-header/div/div/div[2]/div/div/div[3]".format(
                                                    f + 1)))
            )
            flights_list.append(flight.text.replace(' ', ''))
    except TimeoutException:
        pass
    finally:
        print(flights_list)
        print(flights_list.index(flightNumber))
    time.sleep(1)

    try:
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
        low_price = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[@class='flights-table']/div/div[{}]/flights-table-header/div/div[2]".format(localtion_index)
            )))
        low_price.click()
        time.sleep(5)
        many_chirld = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@class="flights-table-fares"]/div/div[1]'
            )))
        many_chirld.click()
        time.sleep(10)
    except Exception as e:
        status = payFail
        errorMsg = '查询航班对应的按钮的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        prices = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="booking-selection"]/article/div[2]/section/div/trips-breakdown/div/div/div[2]'
        )))
        print(prices)
        print(prices.text)
        print(prices.text.split()[1])
        price = float(prices.text.split()[1].replace(',', ''))

        # price = float(prices.text)
        print('这是总的票价', price)
        results["nameList"] = tasks["pnrVO"]["nameList"]
        continues = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="continue"]'))
        )
        continues.click()
        time.sleep(10)
    except Exception as e:
        status = payFail
        errorMsg = '价格页面时候continue出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 改版后的新加代码,点击小黑包的操作
    try:
        black_bag = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@class="priority-boarding-view"]/div[2]/div[2]/div/priority-cabin-bag-card[1]/div/div[3]'
        )))
        black_bag.click()

        time.sleep(4)
        try:
            same_bags = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@class="same-for-all-form"]/div[4]/button[2]'
            )))
            same_bags.click()
            time.sleep(3)
        except Exception as e:
            print("一个人的时候出现异常")
            pass

        continues = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@class="priority-boarding-view"]/div[2]/div[3]/button'
        )))
        continues.click()
        time.sleep(5)
    except Exception as e:
        status = payFail
        errorMsg = '改版后点击小黑包错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        go_it = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="dialog-body-slot"]/dialog-body/seat-map/div[3]/div/div[2]/div/button'
            )))
        go_it.click()
        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '点击go_it出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    if chirld <= 4:
        change_seat_nums = chirld + 1
        if change_seat_nums > len(can_click_seat):
            status = payFail
            errorMsg = '当前剩余座位数量不足以选座，请人工处理'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results
        else:
            s = can_click_seat[-change_seat_nums:]
    else:
        change_seat_nums = chirld + 2
        if change_seat_nums > len(can_click_seat):
            status = payFail
            errorMsg = '当前剩余座位数量不足以选座，请人工处理'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, "座位不够，人工处理"))
            return results
        else:
            s = can_click_seat[-change_seat_nums:]
    print(s)

    # 选座位
    for ss in s:
        print(ss)
        # 执行js脚本
        select_seat_js = """document.querySelector("#scrollable > div.seat-map > div > div.seat-map-rows > div:nth-child({}) > div:nth-child({}) > span > span").click()"""
        if ss[-1] == 'A':
            driver.execute_script(select_seat_js.format(int(ss[:2]) + 6, 1))
        elif ss[-1] == 'B':
            driver.execute_script(select_seat_js.format(int(ss[:2]) + 6, 2))
        elif ss[-1] == 'C':
            driver.execute_script(select_seat_js.format(int(ss[:2]) + 6, 3))
        elif ss[-1] == 'D':
            driver.execute_script(select_seat_js.format(int(ss[:2]) + 6, 5))
        elif ss[-1] == 'E':
            driver.execute_script(select_seat_js.format(int(ss[:2]) + 6, 6))
        elif ss[-1] == 'F':
            driver.execute_script(select_seat_js.format(int(ss[:2]) + 6, 7))

    # jquery_js = """var headID = document.getElementsByTagName("head")[0];
    # var newScript = document.createElement('script');
    # newScript.type = 'text/javascript';
    # newScript.src = 'https://code.jquery.com/jquery-1.10.0.min.js';
    # headID.appendChild(newScript);"""
    # driver.execute_script(jquery_js)
    # time.sleep(2)
    # s = random.sample(can_click_seat, 3)
    # data_dic = [
    #     {"paxNum": 0, "journeyNum": 0, "segmentNum": 0, "designator": s[0]},
    #     {"paxNum": 1, "journeyNum": 0, "segmentNum": 0, "designator": s[1]},
    #     {"paxNum": 2, "journeyNum": 0, "segmentNum": 0, "designator": s[2]}
    # ]
    # print(data_dic)
    # print(json.dumps(data_dic))
    # bgJS = """return $.ajax({type: "POST",url: "https://desktopapps.ryanair.com/v4/en-us/seat",data:"""  + json.dumps(data_dic) + """,async: false}).responseText;"""
    # # bgJS = """$.ajax({type: "POST",url: "https://desktopapps.ryanair.com/v4/en-us/seat",data:"""  + json.dumps(data_dic) + """,async: false})"""
    #
    # print(bgJS)
    # res = driver.execute_script(bgJS)
    # print(res)
    # print(res.text)

    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    #     'Content-Type': 'application/json',
    #     'x-session-token':token
    # }

    # uurl = 'https://desktopapps.ryanair.com/v4/en-us/seat'
    # seats = requests.post(uurl,headers = headers,data=json.dumps(datas))
    # print(seats.text)
    # print(json.dumps(seats.text))
    # time.sleep(6)

    time.sleep(2)
    try:
        review = wait.until(EC.presence_of_element_located((
            By.XPATH,
            '//*[@id="dialog-body-slot"]//following-sibling::div[1]/dialog-footer/div/dialog-overlay-footer/div/div[3]/disabled-tooltip/span/ng-transclude/tooltip-target/button-spinner/button'
        )))
        review.click()
        time.sleep(3)
    except Exception as e:
        status = payFail
        errorMsg = '选择座位后点击review按钮出错，可重跑'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        confirm = wait.until(EC.presence_of_element_located((
            By.XPATH,
            '//*[@class="dialog-footer"]/dialog-footer/div/dialog-overlay-footer/div/div[3]/disabled-tooltip/span/ng-transclude/tooltip-target/button-spinner/button'
        )))
        confirm.click()
        time.sleep(2)
        try:
            nothank = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="dialog-body-slot"]/dialog-body/confirm-seats/div[2]/div/div/div[3]/div[3]/a'
            )))
            nothank.click()
            time.sleep(3)
        except Exception as e:
            status = payFail
            errorMsg = '点击nothanks的时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            # pass
    except Exception as e:
        status = payFail
        errorMsg = '确认座位时出错'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 点击行李按钮
    try:
        weight_list = []
        passengerVOList = tasks["passengerVOList"]
        passengerVOList = sorted(passengerVOList, key=lambda dic: dic["birthday"])
        for weight in passengerVOList:
            baggageWeight = weight["baggageWeight"]
            weight_list.append(baggageWeight)
        bag_prices = 0
        if sum(weight_list) != 0:
            add_bag_click = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="extras-section__body"]/extras-card[2]/div/div'))
            )
            add_bag_click.click()
            time.sleep(3)
            for w in range(len(weight_list)):
                print(weight_list[w])
                if weight_list[w] == 0:
                    pass
                elif 0 <= weight_list[w] <= 20:
                    first_bag = wait.until(
                        # EC.presence_of_element_located((By.XPATH,'//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[1]/div/div[{}]'.format(w+1,w+1)))
                        EC.presence_of_element_located((By.XPATH,
                                                        "//*[@class='equipment-passengers']/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div/bags-selector-icon[{}]/div/div[2]".format(
                                                            w + 1, 1)))
                    )
                    first_bag.click()
                    time.sleep(1)
                elif 20 < weight_list[w] <= 40:
                    first_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//*[@class='equipment-passengers']/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div/bags-selector-icon[{}]/div/div[2]".format(
                                                            w + 1, 1))))
                    sec_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//*[@class='equipment-passengers']/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div/bags-selector-icon[{}]/div/div[2]".format(
                                                            w + 1, 2))))
                    first_bag.click()
                    time.sleep(1)
                    sec_bag.click()
                    time.sleep(1)
                else:
                    first_bag = wait.until(
                        # EC.presence_of_element_located((By.XPATH,'//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[1]/div/div[{}]'.format(w + 1, w + 1)))
                        EC.presence_of_element_located((By.XPATH,
                                                        "//*[@class='equipment-passengers']/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div/bags-selector-icon[{}]/div/div[2]".format(
                                                            w + 1, 1))))
                    sec_bag = wait.until(
                        # EC.presence_of_element_located((By.XPATH,'//*[@id="dialog-body-slot"]/dialog-body/bag-selection/div/div/div[2]/div/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div[1]/bags-selector-icon[2]/div/div[{}]'.format(w + 1, w + 1)))
                        EC.presence_of_element_located((By.XPATH,
                                                        "//*[@class='equipment-passengers']/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div/bags-selector-icon[{}]/div/div[2]".format(
                                                            w + 1, 2))))
                    third_bag = wait.until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//*[@class='equipment-passengers']/bags-per-person[{}]/div/div[3]/div/single-bag-in-row/div/bags-selector-icon[{}]/div/div[2]".format(
                                                            w + 1, 3))))
                    first_bag.click()
                    time.sleep(1)
                    sec_bag.click()
                    time.sleep(1)
                    third_bag.click()
                    time.sleep(1)
            bag_price = wait.until(EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="dialog-body-slot"]//following-sibling::div[1]/dialog-footer/dialog-overlay-footer/div/div[3]/div/span[2]'
            )))
            bag_prices = float(bag_price.text.split()[1].replace(',', ''))
            print('这是行李的总价格', bag_prices)
            confirms = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="dialog-body-slot"]//following-sibling::div[1]/dialog-footer/dialog-overlay-footer/div/div[3]/disabled-tooltip/span/ng-transclude/tooltip-target/button-spinner/button'))
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
    results["baggagePrice"] = bag_prices
    total_price = float(price) + float(bag_prices)
    print('这是票价和行李价格总价', total_price)

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
        errorMsg = '点击check_out时候出现异常'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    try:
        login_button = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@ui-sref="login"]'
        )))
        login_button.click()
        time.sleep(8)
    except Exception as e:
        status = payFail
        errorMsg = '点击登录按钮时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    # 获取账号密码输入框以及确认登陆按钮
    try:
        usernames = tasks["pnrVO"]["accountUsername"]
        passwords = tasks["pnrVO"]["accountPassword"]
        email_address = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@type="email"]'
            ))
        )
        email_password = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@type="password"]'
            ))
        )
        email_address.send_keys(usernames)
        time.sleep(1)
        email_password.send_keys(passwords)
        time.sleep(1)
        login_button = wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@type="submit"]'
            ))
        )
        login_button.click()
        time.sleep(8)
    except Exception as e:
        status = payFail
        errorMsg = '点击登录或者输入账号密码的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results

    passge = tasks["passengerVOList"]
    passge = sorted(passge, key=lambda dic: dic["birthday"])
    now_year = int(time.strftime("%Y", time.localtime()))
    adults = []
    chirlds = []
    for i in passge:
        birthday = int(i["birthday"][:4])
        if now_year - birthday > 11:
            adults.append(i)
        else:
            chirlds.append(i)

    # 填写成人信息
    for i in range(len(adults)):
        try:
            gender = adults[i]["sex"]
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
            first_names = adults[i]["name"].split('/')[0]
            last_names = adults[i]["name"].split('/')[1]
            first_name = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[2]/input".format(
                                                    i + 1)))
            )
            first_name.send_keys(last_names)
            time.sleep(2)

            last_name = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[3]/input".format(
                                                    i + 1)))
            )
            last_name.send_keys(first_names)
            time.sleep(3)
        except Exception as e:
            status = payFail
            errorMsg = '输入成人姓名时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results

    # 填写儿童信息
    for j in range(len(chirlds)):
        try:
            chirld_first_name_input = wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[{}]/input".format(
                    adult + teen + j + 1, 1)
            )))
            chirld_first_name_input.send_keys(chirlds[j]["name"].split('/')[1])
            time.sleep(1)
            chirld_last_name_input = wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@name='passengersForm']/passenger-input-group[{}]/div/ng-form/div/div[{}]/input".format(
                    adult + teen + j + 1, 2)
            )))
            chirld_last_name_input.send_keys(chirlds[j]["name"].split('/')[0])
        except Exception as e:
            status = payFail
            errorMsg = '输入儿童姓名时候出现错误'
            results["status"] = status
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results

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
        time.sleep(2)
    except Exception as e:
        status = payFail
        errorMsg = '选择手机号码所属地或输入手机号的时候出现错误'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{},{}'.format(errorMsg, e))
        return results
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
            logger_crawl.error('{},{}'.format(errorMsg, " -> 无效卡"))
            return results
    except Exception as e:
        pass

    try:
        cvv_num = tasks["payPaymentInfoVo"]["cardVO"]["cvv"]
        cardholder = tasks["payPaymentInfoVo"]["cardVO"]["firstName"] + ' ' + tasks["payPaymentInfoVo"]["cardVO"][
            "lastName"]
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
        years = wait.until(
            EC.presence_of_element_located((
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
    include_tax_price = (total_ticket_price * 100) - (bag_prices * 100)
    results["price"] = include_tax_price / 100
    print('这是减去行李之后的价格，包含手续费和票价', include_tax_price / 100)

    target_price = (int(tasks["targetPrice"]) + 1) * passengerCount
    print(json.dumps(results))
    if price <= target_price:
        print(print(json.dumps(results)))
        try:
            # 点击支付按钮
            pay_button = driver.find_element_by_xpath('//*[@class="cta"]/button')
            pay_button.click()
            time.sleep(8)
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

                # 支付成功之后，获取票号
                try:
                    pnr = wait.until(EC.presence_of_element_located((
                        By.XPATH, "//*[@class='booking-details__summary']/div[3]/div[2]/span"
                    )))
                    pnr = pnr.text
                    logger_crawl.info("这是票号，{}".format(pnr))
                    if pnr != "":
                        errorMsg = '支付成功'
                        results["pnr"] = pnr
                        results["status"] = bookStatus["PaySuccess"]
                        results["errorMessage"] = errorMsg
                        logger_crawl.error('{},{}'.format(errorMsg, results))
                        input("输入点东西")
                        return results
                    else:
                        errorMsg = '支付成功，但是没有获取到票号'
                        results["pnr"] = pnr
                        results["status"] = bookStatus["PayFailAfterSubmitCard"]
                        results["errorMessage"] = errorMsg
                        logger_crawl.error('{},{}'.format(errorMsg, results))
                        input("输入点东西")
                        return results
                except Exception as e:
                    errorMsg = '获取票号时候时候出现错误'
                    results["status"] = bookStatus["PayFailAfterSubmitCard"]
                    results["errorMessage"] = errorMsg
                    logger_crawl.error('{},{}'.format(errorMsg, e))
                    return results
            except Exception as e:
                errorMsg = '支付卡出现错误，卡未授权'
                results["status"] = payFail
                results["errorMessage"] = errorMsg
                logger_crawl.error('{},{}'.format(errorMsg, e))
                return results

        except Exception as e:
            errorMsg = '点击同意按钮时候出现错误'
            results["status"] = bookStatus["PayFailAfterSubmitCard"]
            results["errorMessage"] = errorMsg
            logger_crawl.error('{},{}'.format(errorMsg, e))
            return results
    else:
        status = payFail
        errorMsg = '出票时候，票总价大于传回来的价格'
        results["status"] = status
        results["errorMessage"] = errorMsg
        logger_crawl.error('{}'.format(errorMsg))
        return results


if __name__ == '__main__':
    # while True:
    flag_test = False
    if flag_test:
        # 获取任务
        task_response = get_task()
    else:
        with open("./test.json", "r", encoding="utf-8") as f:
            task_response = json.load(f)
            task_response = json.dumps(task_response)
    if json.loads(task_response)["status"] == 'Y':
        task_response = json.loads(task_response)
        logging.info(task_response)
        print(json.dumps(task_response))
        datas = task_response["data"]
        result["accountPassword"] = datas["pnrVO"]["accountPassword"]
        result["accountType"] = datas["pnrVO"]["accountType"]
        result["accountUsername"] = datas["pnrVO"]["accountUsername"]
        result["cardName"] = datas["pnrVO"]["cardName"]
        result["cardNumber"] = datas["pnrVO"]["cardNumber"]
        result["checkStatus"] = datas["pnrVO"]["checkStatus"]
        result["createTaskStatus"] = datas["pnrVO"]["createTaskStatus"]
        result["linkEmail"] = datas["pnrVO"]["linkEmail"]
        result["linkEmailPassword"] = datas["pnrVO"]["linkEmailPassword"]
        result["linkPhone"] = datas["pnrVO"]["linkPhone"]
        result["targetCur"] = datas["pnrVO"]["targetCur"]
        result["nameList"] = datas["pnrVO"]["nameList"]
        result["payTaskId"] = datas["pnrVO"]["payTaskId"]
        result["sourceCur"] = datas["pnrVO"]["sourceCur"]
        result["machineCode"] = 'frbendi'
        result["clientType"] = 'FR_PAY_CLIENT'
        result["promo"] = None
        result["creditEmail"] = None
        result["creditEmailCost"] = None

        result["pnr"] = None
        result["price"] = None
        result["baggagePrice"] = None
        result["errorMessage"] = None
        result["status"] = None
        passengerCount = datas["passengerCount"]
        passenger = datas["passengerVOList"]
        chirld = 0
        teen = 0
        adult = 0
        baby = 0
        now_time_year = int(time.strftime("%Y", time.localtime()))
        for p in passenger:
            birthdays_year = int(p["birthday"][:4])  # 获取出身年份
            # years = int(now_time_year) - birthdays_year
            years = now_time_year - birthdays_year  # 年龄大小
            if 2 < years <= 11:
                chirld += 1
            elif 12 <= years <= 15:  # fix bug: 判断漏掉了12岁
                teen += 1
            elif years < 2:
                print("出现婴儿票，请人工处理")
                errorMsg = "出现婴儿票，请人工处理"
                status = payFail
                result["status"] = status
                result["errorMessage"] = errorMsg
                logger_crawl.error('{},{}'.format(errorMsg, "婴儿票报错信息"))
                send_data(result)  # 回填数据
            else:
                adult += 1
        print(chirld)
        print(teen)
        print(adult)

        if chirld < 1:  # 没有儿童的情况
            res = get_indexs(datas, adult, teen, chirld, result, passengerCount)
            print(json.dumps(res))
            send_data(res)
        else:  # 有儿童的情况
            flight_number = datas["depFlightNumber"]
            orgin = datas["depAirport"]
            Destination = datas["arrAirport"]
            date = datas["depDate"]
            task = get_data(adult, teen, chirld, date, Destination, orgin)
            data = parse_data(task)
            print(data)
            token = get_flight_data(data, flight_number, datas, result)
            print(token)
            can_click_seat = get_seat(token, datas, result)
            print(can_click_seat)
            back_data = get_index(orgin, Destination, date, adult, teen, chirld, can_click_seat, datas, result,
                                  passengerCount)
            print(json.dumps(back_data))
            send_data(back_data)
    else:
        print("没有任务，休息60S")
        time.sleep(60)
