import datetime
import requests
import json
from bs4 import BeautifulSoup


class Parser:
    main_url = "https://moodle.astanait.edu.kz/?lang=en"
    security_url = "https://moodle.astanait.edu.kz/user/managetoken.php"
    api_url = "https://moodle.astanait.edu.kz/webservice/rest/server.php"
    assign_url = "https://moodle.astanait.edu.kz/mod/assign/view.php?id="

    async def get_token_and_userid(self, cookies):
        session = requests.Session()
        src = session.get(self.security_url, cookies=cookies)
        soup = BeautifulSoup(src.text, 'lxml')
        token = soup.find('tbody').find('tr').find('td').text
        userid = soup.find('div', class_='popover-region collapsed popover-region-notifications').get('data-userid')
        return token, userid

    async def get_courses(self, cookies):
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

    async def get_grades(self, id_subject, webservice_token, user_id):
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

    async def get_deadlines(self, webservice_token):
        args = {
            'moodlewsrestformat': 'json',
            'wstoken': webservice_token,
            'wsfunction': 'mod_assign_get_assignments'
        }
        response = json.loads(requests.get(self.api_url, params=args).text)

        time_now = datetime.datetime.now().timestamp()

        deadlines = {}

        for course in response['courses']:
            deadlines.update({
                course['id']: {}
            })
            for assign in course['assignments']:
                # duedate = datetime.datetime.fromtimestamp(assign['duedate']).replace(microsecond=0)
                duedate = assign['duedate']
                if duedate > time_now:
                    id_assign = assign['cmid']
                    name = assign['name']
                    deadline = duedate
                    deadlines[course['id']].update({
                        id_assign: {
                            'name': name,
                            'deadline': deadline,
                            'link': f"{self.assign_url}{id_assign}"
                        }
                    })

        return deadlines
