import os
import pickle
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


# from fake_useragent import UserAgent


def auth_microsoft(barcode, password):
    options = webdriver.ChromeOptions()
    # options.add_argument(f"user-agent={UserAgent().chrome}")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/107.0.0.0 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(options=options)

    email_field = (By.ID, "i0116")
    password_field = (By.ID, "i0118")
    next_button = (By.ID, "idSIButton9")
    browser.get('https://moodle.astanait.edu.kz/auth/oidc/')
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(email_field)).send_keys(f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f""
                                                                                        f"{barcode}@astanait.edu.kz")
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(next_button)).click()
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(password_field)).send_keys(password)
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(next_button)).click()
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(next_button)).click()

    if not os.path.exists("moodle/cookies"):
        os.mkdir("moodle/cookies")
    pickle.dump(browser.get_cookies(), open(f"moodle/cookies/{barcode}", "wb"))
    browser_cookies = browser.get_cookies()
    browser.close()
    browser.quit()


def auth_with_cookies(barcode, password):
    session = requests.Session()
    cookies = {}
    for cookie in pickle.load(open(f"moodle/cookies/{barcode}", 'rb')):
        cookies[cookie['name']] = cookie['value']
    response = session.get('https://moodle.astanait.edu.kz/?lang=en', cookies=cookies)
    if "You are not logged in" in response.text:
        print("Cookies are invalid. Trying to log in again...")
        auth_microsoft(barcode, password)
        auth_with_cookies(barcode, password)
    else:
        print("We are authorized.")
        return cookies


class SignIn:
    main_url = "https://moodle.astanait.edu.kz/"

    def __init__(self, data):
        self.barcode = data['barcode']
        self.password = data['password']

    def login_moodle(self):
        try:
            return auth_with_cookies(self.barcode, self.password)
        except FileNotFoundError:
            auth_microsoft(self.barcode, self.password)
            return auth_with_cookies(self.barcode, self.password)
