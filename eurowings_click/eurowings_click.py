# # -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class EnuCrawl:

    def __init__(self, username=u'18810298352', password=u'jiushini123', dep=u'西藏', arr=u'澳门', depDate=u'2019-01-15'):
        # 登录的用户名
        self.username = username
        # 登录的密码
        self.password = password
        # 起始出发地
        self.dep = dep
        # 到达目的地
        self.arr = arr
        # 出发时间
        self.depDate = depDate

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

    def _login(self):
        option = 'C:\Program Files\Chrome\chromedriver.exe'
        self.drive = webdriver.Chrome(executable_path=option)
        # 窗口最大化
        self.drive.maximize_window()
        # 登录url网址
        self.drive.get('https://mobile.eurowings.com/booking/Select.aspx')
        # 点击去登陆按钮
        WebDriverWait(self.drive, 20).until(EC.presence_of_element_located(
            (By.XPATH, '//span[@class="icon-menu"]')))
        self.drive.find_element_by_xpath('//span[@class="icon-menu"]/..').click()
        # 更改语言为英语
        # self.is_language()
        # 等待login登录按钮显示出来
        WebDriverWait(self.drive, 50).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@class="login-form-head"]/span[2]')))
        self.drive.find_element_by_xpath('//*[@class="login-form-head"]/span[2]').click()
        # 等待用户名和密码框出现
        WebDriverWait(self.drive, 50).until(EC.presence_of_element_located(
            (By.XPATH, '//span[@class="footer-icon icon-ico-arrow-close"]')))
        # 输入用户名
        self.drive.find_element_by_xpath('//input[@id="user"]').send_keys(self.username)
        # 输入密码
        self.drive.find_element_by_xpath('//input[@id="password"]').send_keys(self.password)
        # 等待输入用户名成功的提示
        WebDriverWait(self.drive, 20).until(EC.presence_of_element_located(
            By.XPATH('//div[@class="input-box link valid"][1]')))
        # 等待密码属于成功的提示
        WebDriverWait(self.drive, 20).until(EC.presence_of_element_located(
            By.XPATH('//div[@class="input-box link valid"][2]')))
        # 点击登录
        self.drive.find_element_by_xpath('//*[@id="loginUser"]').click()

    def _start(self):
        # 登录
        self._login()


if __name__ == '__main__':
    en = EnuCrawl()
    en._start()
