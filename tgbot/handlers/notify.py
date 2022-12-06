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
        cookies = json.loads(await db.get_key(user_id, 'cookies'))
        while not await is_cookies_valid(cookies):
            barcode, password = await db.get_user_data(user_id)
            cookies = await auth_microsoft(barcode, password)

        courses_dict = await parser.get_courses(cookies)
        grades_dict = json.loads(await db.get_key(user_id, 'grades'))
        new_grades_dict = {}
        token, userid = await db.get_keys(user_id, 'webservice_token', 'moodle_userid')
        token = decrypt(token, userid)

        for id_course in courses_dict.keys():
            new_grades_dict.update({
                id_course: await parser.get_grades(id_course, token, userid)
            })

        text = "Updated grades:\n\n"
        isNewGrade = False
        for id_course in new_grades_dict.keys():
            diff = new_grades_dict[id_course].items() - grades_dict[id_course].items()
            if len(diff) != 0:
                isNewGrade = True
                link_course = courses_dict[id_course]['link']
                name_course = courses_dict[id_course]['name']
                text += f"  <a href=\"{link_course}\">{name_course}</a>:\n"
                for el in diff:
                    itemname, grade = el
                    old_grade = grades_dict[id_course].get(itemname)
                    text += f"      {itemname} / {old_grade} -> {grade}\n"
                text += "\n"
        if isNewGrade:
            await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
        else:
            await bot.send_message(chat_id=user_id, text="Bot didn't find any changes")

        await db.set_keys(
            user_id,
            {
                'cookies': json.dumps(cookies),
                'courses': json.dumps(courses_dict),
                'grades': json.dumps(new_grades_dict)
            }
        )


def register_schedulers(bot, scheduler):
    now = datetime.datetime.now()
    hours, minutes = divmod(ceil(now.minute / 30) * 30, 60)
    rounded_time = (now + datetime.timedelta(hours=hours)).replace(minute=minutes, second=0).strftime(
        "%Y-%m-%d %H:%M:%S")
    scheduler.add_job(auto_update, 'interval', minutes=30, start_date=rounded_time, kwargs={'bot': bot})
