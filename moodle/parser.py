import requests
import json
from bs4 import BeautifulSoup

from moodle.login import SignIn


class Parser:
    main_url = "https://moodle.astanait.edu.kz/?lang=en"
    security_url = "https://moodle.astanait.edu.kz/user/managetoken.php"
    api_url = "https://moodle.astanait.edu.kz/webservice/rest/server.php"

    def __init__(self, barcode, password):
        self.barcode, self.password = barcode, password

    def get_cookies(self):
        signin = SignIn(self.barcode, self.password)
        cookies = signin.login_moodle()
        return cookies

    def get_token_and_userid(self, cookies):
        session = requests.Session()
        src = session.get(self.security_url, cookies=cookies)
        soup = BeautifulSoup(src.text, 'lxml')
        token = soup.find('tbody').find('tr').find('td').text
        userid = soup.find('div', class_='popover-region collapsed popover-region-notifications').get('data-userid')
        return token, userid

    def get_courses(self, cookies):
        session = requests.Session()
        src = session.get(self.main_url, cookies=cookies)
        soup = BeautifulSoup(src.text, 'lxml')
        links = soup.find_all('a')
        courses = {}
        for el in links:
            if el.get('data-parent-key') == 'mycourses':
                name_subject = el.select_one('span.media-body').text
                id_subject = el.get('data-key')
                link_subject = el.get('href')
                courses.update({id_subject: {'id': id_subject, 'name': name_subject, 'link': link_subject}})
        return courses

    def get_grades(self, id_subject, webservice_token, user_id):
        args = {
            'moodlewsrestformat': 'json',
            'wstoken': webservice_token,
            'wsfunction': 'gradereport_user_get_grades_table',
            'userid': user_id,
            'courseid': id_subject
        }
        response = requests.get(self.api_url, params=args)
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
            grades.update({
                itemname: grade
            })
        return grades
