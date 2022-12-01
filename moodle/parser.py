import requests
import json
from bs4 import BeautifulSoup
from moodle.login import SignIn
from tgbot.utils.config import load_config
from tgbot.utils.logger import logger


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
        links = soup.find_all('a')
        # courses = ""
        courses = {}
        for el in links:
            if el.get('data-parent-key') == 'mycourses':
                name_subject = el.select_one('span.media-body').text
                id_subject = el.get('data-key')
                link_subject = el.get('href')
                # text += f"Name - {name_subject}\n" \
                #         f"ID - {id_subject}\n" \
                #         f"Link - {link_subject}\n\n"
                courses.update({id_subject: {'id': id_subject, 'name': name_subject, 'link': link_subject}})
        return courses

    def get_grades(self, id_subject):
        data = load_config()
        args = {
            'moodlewsrestformat': 'json',
            'wstoken': data['webservice_token'],
            'wsfunction': 'gradereport_user_get_grades_table',
            'userid': data['user_id'],
            'courseid': id_subject
        }
        response = requests.get("https://moodle.astanait.edu.kz/webservice/rest/server.php", params=args)
        text = json.loads(response.text)['tables'][0]['tabledata']
        grades = {}
        for el in text:
            if el.__class__ is list or len(el) in [0, 2]:
                continue
            itemname = BeautifulSoup(el['itemname']['content'], 'lxml').text
            grade = el['grade']['content']
            strings = ['Включая незаполненные оценки.', '(not to edit)', 'Include empty grades.']
            for string in strings:
                itemname = itemname.replace(string, '')
                # print(f"{itemname} - {grade}")
            grades.update({
                itemname: grade
            })
        return grades

    # def get_grades(self, id_subject):
    #     cookies = self.get_cookies()
    #     session = requests.Session()
    #     src = session.get(f"{self.grade_url}{id_subject}", cookies=cookies)
    #     soup = BeautifulSoup(src.text, 'lxml')
    #     # Register Grades
    #     items_register = soup.find_all('span', {'class': 'gradeitemheader'}, limit=4)
    #     grades_register = soup.select('td.level3.column-grade')
    #     text = ""
    #     for i in range(len(items_register)):
    #         # print(f"{items_register[i].text} - {grades_register[i].text}")
    #         text += items_register[i].text + " - " + grades_register[i].text + "\n"
    #     # Grades
    #     items = soup.find_all(['a', 'span'], {'class': 'gradeitemheader'})
    #     del items[0:5]
    #     del items[-1]
    #     grades = soup.select('td.level2.leveleven.item.b1b.itemcenter.column-grade')
    #     for i in range(len(items)):
    #         # print(f"{items[i].text} - {grades[i].text}")
    #         text += items[i].text + " - " + grades[i].text + "\n"
    #     return text
