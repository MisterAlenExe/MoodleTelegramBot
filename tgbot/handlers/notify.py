import json
import datetime
from math import ceil

from aiogram import Bot

from database import Database, decrypt
from functions.login import is_cookies_valid, auth_microsoft
from functions.parser import Parser


async def auto_update(bot: Bot):
    db = Database()
    parser = Parser()

    for user_id in await db.get_all_users():
        # cookies = json.loads(await db.get_key(user_id, 'cookies'))
        # while not await is_cookies_valid(cookies):
        #     barcode, password = await db.get_user_data(user_id)
        #     cookies = await auth_microsoft(barcode, password)

        token, userid = await db.get_keys(user_id, 'webservice_token', 'moodle_userid')
        token = decrypt(token, userid)

        courses_dict = await parser.get_courses(token, userid)
        grades_dict = json.loads(await db.get_key(user_id, 'grades'))
        deadlines_dict = json.loads(await db.get_key(user_id, 'deadlines'))

        new_grades_dict = {}
        for id_course in courses_dict.keys():
            new_grades_dict.update({id_course: await parser.get_grades(id_course, token, userid)})
        new_deadlines_dict = await parser.get_deadlines(token)

        text_grades = "Updated grades:\n\n"
        text_deadlines = "Updated deadlines:\n\n"
        isNewGrade = False
        isNewDeadline = False

        deadlines = {}

        for id_course in courses_dict.keys():
            diff = new_grades_dict[id_course].items() - grades_dict[id_course].items()
            if len(diff) != 0:
                isNewGrade = True
                link_course = courses_dict[id_course]['link']
                name_course = courses_dict[id_course]['name']
                text_grades += f"  <a href=\"{link_course}\">{name_course}</a>:\n"
                for el in diff:
                    itemname, grade = el
                    old_grade = grades_dict[id_course].get(itemname)
                    text_grades += f"      {itemname} / {old_grade} -> {grade}\n"
                text_grades += "\n"

            for id_assign, assign in new_deadlines_dict[id_course].items():
                if id_assign not in deadlines_dict[id_course].keys() \
                        or assign['name'] != deadlines_dict[id_course][id_assign]['name'] \
                        or assign['deadline'] != deadlines_dict[id_course][id_assign]['deadline']:
                    isNewDeadline = True
                    deadlines.update({id_course: {
                        id_assign: {
                            'name': assign['name'],
                            'deadline': assign['deadline'],
                            'link': assign['link']
                        }}
                    })

        time_now = datetime.datetime.now().replace(microsecond=0)

        for id_course, assigns_dict in deadlines.items():
            link_course = courses_dict[id_course]['link']
            name_course = courses_dict[id_course]['name']
            text_deadlines += f"<a href=\"{link_course}\">{name_course}</a>:\n"
            for id_assign, assign in assigns_dict.items():
                name_assign = assign['name']
                duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
                deadline = duedate.strftime("%A, %d %B, %I:%M %p")
                remaining = duedate - time_now
                link_assign = assign['link']

                text_deadlines += f"  <a href=\"{link_assign}\">{name_assign}</a>\n"
                text_deadlines += f"  {deadline}\n"
                text_deadlines += f"  Remaining: {remaining}\n\n"

        if isNewGrade:
            await bot.send_message(chat_id=user_id, text=text_grades, parse_mode='HTML')
        else:
            await bot.send_message(chat_id=user_id, text="Bot didn't find any changes")
        if isNewDeadline:
            await bot.send_message(chat_id=user_id, text=text_deadlines, parse_mode='HTML')
        else:
            await bot.send_message(chat_id=user_id, text="Bot didn't find any changes")

        await db.set_keys(user_id, {
            'courses': json.dumps(courses_dict),
            'grades': json.dumps(new_grades_dict),
            'deadlines': json.dumps(new_deadlines_dict)
        })


def register_schedulers(bot, scheduler):
    # now = datetime.datetime.now()
    # hours, minutes = divmod(ceil(now.minute / 30) * 30, 60)
    # rounded_time = (now + datetime.timedelta(hours=hours)).replace(minute=minutes, second=0).strftime(
    #     "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    time_start = (now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=10 - now.minute % 10)).strftime(
        "%Y-%m-%d %H:%M:%S")
    scheduler.add_job(auto_update, 'interval', minutes=10, start_date=time_start, kwargs={'bot': bot})
