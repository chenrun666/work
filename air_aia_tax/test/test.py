import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



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



def drawback(driver, order, config):
    url = "https://support.airasia.com/s/customcontactsupport?language=zh_CN"
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.ID, '46:2;a'))
    )

    feed_options = Select(driver.find_element_by_id('46:2;a'))
    time.sleep(1)
    feed_options.select_by_value("Enquiry/Request")
    time.sleep(2)
    button = driver.find_element_by_xpath('//*[@id="refundCase"]/div[3]/div[1]/div[4]/div[15]/button[1]')
    button.click()
    time.sleep(4)


if __name__ == '__main__':
    driver = init_driver()
    drawback(driver,1, 1)


