from environs import Env
import pickle
import time
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def load_config(path: str = None):
    env = Env()
    env.read_env(path)
    data = {
        'barcode': env.str("BARCODE"),
        'password': env.str("PASSWORD")
    }
    return data


def login_moodle(browser, data):
    email_field = (By.ID, "i0116")
    password_field = (By.ID, "i0118")
    next_button = (By.ID, "idSIButton9")

    browser.get('https://moodle.astanait.edu.kz/auth/oidc/')

    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(email_field)).send_keys(f""
                                                                                        f""
                                                                                        f""
                                                                                        f"{data['barcode']}@astanait"
                                                                                        f".edu.kz")
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(next_button)).click()
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(password_field)).send_keys(data['password'])
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(next_button)).click()
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(next_button)).click()
    time.sleep(5)

    pickle.dump(browser.get_cookies(), open(f"{data['barcode']}_cookies", "wb"))
    browser_cookies = browser.get_cookies()
    browser.close()
    browser.quit()


def login_with_cookies(browser, data):
    session = requests.Session()
    cookies = {}
    for cookie in pickle.load(open(f"{data['barcode']}_cookies", 'rb')):
        cookies[cookie['name']] = cookie['value']
    response = session.get('https://moodle.astanait.edu.kz/', cookies=cookies)
    print(response.text)


def main():
    data = load_config(".env")
    options = Options()
    # options.add_argument(f"user-agent={UserAgent().chrome}")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

    # login_moodle(browser, data)
    login_with_cookies(browser, data)


if __name__ == '__main__':
    main()
