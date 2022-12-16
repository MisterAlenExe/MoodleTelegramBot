import datetime
import aiohttp
import requests
import json
from bs4 import BeautifulSoup


class Parser:
    main_url = "https://moodle.astanait.edu.kz/?lang=en"
    security_url = "https://moodle.astanait.edu.kz/user/managetoken.php"
    api_url = "https://moodle.astanait.edu.kz/webservice/rest/server.php"
    assign_url = "https://moodle.astanait.edu.kz/mod/assign/view.php?id="
    course_url = "https://moodle.astanait.edu.kz/course/view.php?id="

    async def get_token_and_userid(self, cookies):
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.get(self.security_url) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                token = soup.find('tbody').find('tr').find('td').text
                userid = soup.find('div', class_='popover-region collapsed popover-region-notifications').get('data-userid')
                return token, userid

    async def get_courses(self, webservice_token, user_id):
        args = {
            'moodlewsrestformat': 'json',
            'wstoken': webservice_token,
            'wsfunction': 'core_enrol_get_users_courses',
            'userid': user_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=args) as response:
                text = json.loads(await response.text())
                courses = {}

                for course in text:
                    id_subject = str(course['id'])
                    name_subject = course['fullname']
                    link_subject = f"{self.course_url}{id_subject}"
                    courses.update({
                        id_subject: {
                            'id': id_subject,
                            'name': name_subject,
                            'link': link_subject
                        }
                    })
                return courses

    async def get_grades(self, id_subject, webservice_token, user_id):
        args = {
            'moodlewsrestformat': 'json',
            'wstoken': webservice_token,
            'wsfunction': 'gradereport_user_get_grades_table',
            'userid': user_id,
            'courseid': id_subject
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=args) as response:
                text = json.loads(await response.text())['tables'][0]['tabledata']
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

        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=args) as response:
                text = json.loads(await response.text())
                time_now = datetime.datetime.now().timestamp()
                deadlines = {}
                for course in text['courses']:
                    deadlines.update({
                        str(course['id']): {}
                    })
                    for assign in course['assignments']:
                        # duedate = datetime.datetime.fromtimestamp(assign['duedate']).replace(microsecond=0)
                        duedate = assign['duedate']
                        if duedate > time_now:
                            id_assign = assign['cmid']
                            name = assign['name']
                            deadline = duedate
                            deadlines[str(course['id'])].update({
                                str(id_assign): {
                                    'name': name,
                                    'deadline': deadline,
                                    'link': f"{self.assign_url}{id_assign}"
                                }
                            })

                return deadlines
