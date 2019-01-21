import requests
import json, re
import time, random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# 登陆
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# logger = logging.getLogger("tax")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(filename=f'../log/tax{datetime.now().strftime("%Y-%m-%d")}.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def do_login(driver, order):
    # login_url ='https://booking2.airasia.com/bookinglistlogin.aspx'
    # driver.get(login_url)
    # 等待元素加载
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.ID, 'username-input--login'))
    )
    driver.find_element_by_id('username-input--login').send_keys("tianch711092@163.com")
    driver.find_element_by_id('password-input--login').send_keys("Ss136313")
    driver.find_element_by_id('loginbutton').click()


# 获取订单
def get_order(config, type='test'):
    logging.info(f"1.请求任务：")
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*'
    }
    order = {}
    data = {
        "header":
            {
                "carrier": "FD",
                "accountType": "4"
            },
        "params":
            {
                "purpose": "3"
            }
    }
    if type == 'test' or type == '':
        logging.debug("local test")
        # 本地订单
        with open(rf'../order/test.json', encoding='utf-8') as f:
            raworder = f.read()
        order = json.loads(raworder)
    elif type == 'real':
        sid = str(random.randint(1000, 9999))
        url = config['task_url'] + sid
        print("获取信息url:", url)
        raw_order = requests.post(url, timeout=30, headers=headers, data=json.dumps(data)).content
        order_dict = json.loads(raw_order)
        # 错误信息回填
        if order_dict.get('errorCode') == -2:
            raise ValueError(order_dict.get('errorString'))
        order = order_dict
        if order['status'] == 'N':
            print(order['msg'])
            time.sleep(360)
            return False
    print(order)
    logging.info(f"获取到任务：{order}")
    return order


def init_driver():
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "normal"
    chrome_options = webdriver.ChromeOptions()
    chrome_options._arguments = ['disable-infobars']
    chrome_options.add_argument('--disable-extensions')
    prefs = {'profile.managed_default_content_settings.images': 2,
             'disk-cache-size': 4096
             }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--disable-plugins-discovery")
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument("--incognito")
    # chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        chrome_options=chrome_options,
        desired_capabilities=capa
    )
    driver.set_window_size(1366, 768)
    driver.set_window_position(0, 0)
    return driver


# 给定时间，返回最近的时间
def wholePoint(time_str):
    # time_str = '16:25:00', 返回 "16:30"
    temp = time_str.split(":")
    if int(temp[1]) < 30 and abs(int(temp[1]) - 30) > 15:
        return ":".join([temp[0], "00"])

    elif int(temp[1]) < 30 and abs(int(temp[1]) - 30) < 15:
        return ":".join([temp[0], "30"])
    elif int(temp[1]) > 30 and abs(int(temp[1]) - 30) > 15:
        return ":".join([str(int(temp[0]) + 1), "00"])
    else:
        return ":".join([temp[0], "30"])


# 退税申请
def drawback(driver, order, config):
    url = "https://support.airasia.com/s/customcontactsupport?language=zh_CN"
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.ID, '46:2;a'))
    )
    time.sleep(1)
    # 选择反馈类型
    feed_options = Select(driver.find_element_by_id('46:2;a'))
    time.sleep(2)
    feed_options.select_by_value(config['option1'])
    time.sleep(1)
    fName = "".join(order['data']['firstname'].split("\xa0"))
    lName = "".join(order['data']['lastname'].split("\xa0"))
    email = order['data']['email']
    phone = order['data']['mobile']
    pnr = order['data']['bookingNumber']
    flight_num = order['data']['flightNumber']
    depart_date = order['data']['depDate']
    carrierCode = order['data']['carrierCode']
    sub_option = Select(driver.find_element_by_id('58:2;a'))
    sub_option.select_by_value(config['option2'])
    time.sleep(2)
    # 关闭弹出框
    close_btn = driver.find_element_by_xpath(
        "//lightning-icon[@class='close slds-icon-utility-close slds-icon_container']")
    close_btn.click()
    time.sleep(1)

    # 输入标题
    driver.find_element_by_id('97:2;a').send_keys(config['title'])
    # 个人信息
    gender_option = {
        'M': 'Mr.',
        'F': 'Ms.'
    }
    gender = Select(driver.find_element_by_id('112:2;a'))
    if order["data"]["sex"] == "男":
        gender.select_by_value(gender_option.get("M"))
    else:
        gender.select_by_value(gender_option.get("F"))
    # 姓氏
    driver.find_element_by_id('138:2;a').send_keys(fName)
    driver.find_element_by_id('129:2;a').send_keys(lName)
    # 电子邮箱
    driver.find_element_by_id('147:2;a').send_keys(email)
    # 手机号
    regin_code = Select(driver.find_element_by_id('158:2;a'))
    regin_code.select_by_value("China")
    driver.find_element_by_id('input-1').send_keys(phone)
    # 航班信息
    # 预定编号
    driver.find_element_by_id("206:2;a").send_keys(pnr)
    # 航空公司代码
    air_options = Select(driver.find_element_by_id('226:2;a'))
    air_options.select_by_value(carrierCode)
    # 航班号
    driver.find_element_by_id("248:2;a").send_keys(flight_num[2:])
    # 预定起飞时间

    print(depart_date)
    date, time_info = depart_date.split(" ")
    # 返回整点信息
    time_info = wholePoint(time_info)
    driver.find_element_by_id("261:2;a").send_keys(date)
    tmp_obj = driver.find_element_by_id("261:2;a-time")
    tmp_obj.click()
    time.sleep(1)
    # 拼接时间 -> 2:30  -> 02:30
    if len(time_info) != 5:
        time_info = "0" + time_info
    driver.find_element_by_xpath(f"//li[@id='{''.join(time_info.split(':'))}']").click()
    # 备注
    # bak = config['bak'] + email
    # driver.find_element_by_id("523:2;a").send_keys(bak)

    # 选择预定支付渠道
    payment_channel = Select(driver.find_element_by_id('291:2;a'))
    payment_channel.select_by_visible_text(config['option4'])
    time.sleep(1)
    payment_channel.select_by_visible_text(config['option4'])
    time.sleep(1)

    # 提交
    submit = driver.find_element_by_xpath(
        "//button[@class='slds-button slds-button_neutral slds-m-top--medium submit'][1]")
    # 如果点击按钮没有显示在屏幕，需要滑动屏幕将按钮显示出来
    # driver.execute_script("arguments[0].scrollIntoView();", submit)
    data = {
        "header":
            {
                "carrier": "FD",
                "accountType": "4"
            },
        "params":
            {
                "purpose": "3",
                "bookingNumber": pnr,
                "refundNumber": "",
                "status": "1"
            }
    }
    try:
        submit.click()
        # 等待获取数字码
        time.sleep(4)
        # //*[@id="refundCase"]/div/p
        order_num = driver.find_element_by_xpath('//*[@id="refundCase"]/div/p').text
        print("order_num", order_num)
        data = {
            'header': {
                "carrier": "FD",
                "accountType": "4"
            },
            'params': {
                'purpose': "3",
                'status': "1",
                'refundNumber': order_num,
                'bookingNumber': pnr,
            }
        }
        if not order_num:
            data['params']['status'] = -2  # 提交失败-2
    except Exception as e:
        data['params']['status'] = -2  # 提交失败-2
        logging.info(f"提交失败错误信息: {e}")
    print(data)
    logging.info(f"回填信息：{data}")
    return data


def call_back_task(config, data):
    print("开始回填")
    logging.info("开始回填")
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*'
    }
    sid = str(random.randint(1000, 9999))
    url = config['fill_url_test'] + sid
    print(data)
    print(url)
    fillback = requests.post(
        url, headers=headers, data=json.dumps(data))
    print("回填结束")
    print(f'{fillback.text}')
    logging.info(f"回填返回的结果：{fillback.text}")


def csTm_to_strTm(cstTime):
    # Sat, 24 Nov 2018 -> yyyy-mm-dd
    cstTime = cstTime.replace(',', '')
    tempTime = time.strptime(cstTime, '%A %d %B %Y')
    resTime = time.strftime('%Y-%m-%d', tempTime)
    return resTime


# 检查信用账户处理结果
def check_result(driver, order):
    # 登陆
    url = 'https://www.airasia.com/member/myaccount?culture=en-GB'
    # 点击信用账号
    driver.get(url)
    do_login(driver, order)
    js = '''return $('body > app-root > div > main > app-account > div > div > div > div.col.s12.m3.hide-on-small-only.collection.left-nav > app-left-nav > ul > li:nth-child(4) > a').attr('href')'''
    time.sleep(3)
    acct_url = driver.execute_script(js)
    print(f"acct_url: {acct_url}")
    driver.get(acct_url)
    time.sleep(3)
    # 页面 url
    credit_url = 'https://booking2.airasia.com/creditstatus.aspx'
    WebDriverWait(driver, 30).until(
        EC.url_contains(credit_url)
    )
    text = driver.execute_script('''return $("#PaymentInfo > span").text()''')
    if 'No credits available' in text:
        print("信号账号不可用")
        # 返回 报文
    else:
        # 获取可用余额
        mey_text = driver.execute_script('''return $("#accountDetails > tbody > tr > td.creditFont > span").text()''')
        print(mey_text)
        aviale_mey = float(re.findall('(\d+[,.]\d+)', mey_text)[0])
        Curreny = re.findall('([a-zA-Z]+)', mey_text)[0]
        expir_js = '''return $("#creditSummaryBodyRow tr td:contains('Credit') + td ").text()'''
        refund_code_js = '''return $("#creditSummaryBodyRow tr td:contains('Credit')").text()'''
        refund_code = driver.execute_script(refund_code_js)
        refund_code = re.findall('\w+', refund_code)[1]
        print(refund_code)
        tm = driver.execute_script(expir_js)
        date = csTm_to_strTm(tm)
        print(date)
        task_type = '2'  # 1.提交任务 2. 扫余额任务
        data = {
            'header': {
                "carrier": "FD",
                "accountType": "4"},
            'params': {
                'purpose': task_type,
                'balance': aviale_mey,
                'cur': Curreny,
                'expiryDate': date,
                'refundOrderCode': refund_code,
                'email': order['data']['email']
            }
        }
        print(data)
        return data


if __name__ == '__main__':
    # drive = init_driver()
    # with open(rf'../order/test.json', encoding='utf-8') as f:
    #     raworder = f.read()
    # order = json.loads(raworder)
    # check_result(drive, order)

    # 测试返回整点
    # s = '16:46:00'
    # print(wholePoint(s))
    # s_test = "YAN"
    # print("".join(s_test.split()))
    import datetime
    new_time = datetime.datetime.now().strftime("%Y-%m-%d")
    print(new_time)


