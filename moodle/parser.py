import requests
from bs4 import BeautifulSoup
from moodle.login import SignIn
from tgbot.utils.config import load_config


class Parser:
    main_url = "https://moodle.astanait.edu.kz/?lang=en"
    grade_url = "https://moodle.astanait.edu.kz/grade/report/user/index.php?id="

    def get_cookies(self):
        data = load_config()
        signin = SignIn(data)
        return signin.login_moodle()

    def get_courses(self):
        cookies = self.get_cookies()
        session = requests.Session()
        src = session.get(self.main_url, cookies=cookies)
        soup = BeautifulSoup(src.text, 'lxml')
        text = soup.find_all('a')
        for el in text:
            if el.get('data-parent-key') == 'mycourses':
                print(f"ID of subject - {el.get('data-key')}")
                print(f"Link - {el.get('href')}")

    def get_grades(self, id_subject):
        cookies = self.get_cookies()
        session = requests.Session()
        src = session.get(f"{self.grade_url}{id_subject}", cookies=cookies)
        soup = BeautifulSoup(src.text, 'lxml')
        # Register Grades
        items_register = soup.find_all('span', {'class': 'gradeitemheader'}, limit=4)
        grades_register = soup.select('td.level3.column-grade')
        text = ""
        for i in range(len(items_register)):
            # print(f"{items_register[i].text} - {grades_register[i].text}")
            text += items_register[i].text + " - " + grades_register[i].text + "\n"
        # Grades
        items = soup.find_all(['a', 'span'], {'class': 'gradeitemheader'})
        del items[0:5]
        del items[-1]
        grades = soup.select('td.level2.leveleven.item.b1b.itemcenter.column-grade')
        for i in range(len(items)):
            # print(f"{items[i].text} - {grades[i].text}")
            text += items[i].text + " - " + grades[i].text + "\n"
        return text
