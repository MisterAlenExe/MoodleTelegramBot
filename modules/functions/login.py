import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from ..tgbot.utils.logger import logger


async def auth_microsoft(barcode, password):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/107.0.0.0 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(chrome_options=options)

    email_field = (By.ID, "i0116")
    password_field = (By.ID, "i0118")
    next_button = (By.ID, "idSIButton9")
    browser.get('https://moodle.astanait.edu.kz/auth/oidc/')
    wait = WebDriverWait(browser, 10)
    try:
        wait.until(ec.element_to_be_clickable(email_field)).send_keys(f"{barcode}@astanait.edu.kz")
        wait.until(ec.element_to_be_clickable(next_button)).click()
        wait.until(ec.element_to_be_clickable(password_field)).send_keys(password)
        wait.until(ec.element_to_be_clickable(next_button)).click()
        wait.until(ec.element_to_be_clickable(next_button)).click()
    except:
        pass

    browser_cookies = browser.get_cookies()
    browser.close()
    browser.quit()

    cookies = {}
    for cookie in browser_cookies:
        cookies[cookie['name']] = cookie['value']
    return cookies


async def is_cookies_valid(cookies):
    try:
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.get('https://moodle.astanait.edu.kz/?lang=en') as response:
                if "You are not logged in" in await response.text():
                    return False
                else:
                    return True
    except aiohttp.ClientConnectorError:
        logger.error("Connection can not be established.")
        return False
