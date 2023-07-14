# stdlib
import json
import re

# third party
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager



class YahooSelenium(object):

    LOGIN_URL = "https://login.yahoo.com"
    YAHOO_FINANCE_URL = "https://finance.yahoo.com"

    def __init__(self, username: str = None, password: str = None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        if username is not None and password is not None:
            self._login(username, password)
        else:
            self._home()
        self.cookies = self._get_cookies()
        self.crumb = self._get_crumb()
        self.driver.quit()
            
    def _get_cookies(self):
        return self.driver.get_cookies()
    
    def _get_crumb(self):
        text = self.driver.page_source
        path = re.compile(r'window\.YAHOO\.context = ({.*?});', re.DOTALL)
        match = re.search(path, text)
        if match:
            dct = json.loads(match.group(1))
            crumb = dct.get('crumb', None)
            if crumb is not None:
                return crumb.replace("\\u002F", "/")
        
        return None

    def _login(self, username: str, password: str):
        self.driver.execute_script("window.open('{}');".format(self.LOGIN_URL))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.XPATH, "//input[@id='login-signin']").click()
        password_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-passwd"))
        )
        password_element.send_keys(password)
        self.driver.find_element(By.XPATH, "//button[@id='login-signin']").click()
        
    def _home(self):
        self.driver.get(self.YAHOO_FINANCE_URL)
