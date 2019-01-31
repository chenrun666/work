from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class OpenBrowser(object):
    def __init__(self):
        # 初始化浏览器
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
        driver = webdriver.Chrome(
            chrome_options=chrome_options,
            desired_capabilities=capa
        )
        driver.set_window_size(1366, 768)
        driver.set_window_position(0, 0)

        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
