import json
import datetime

from aiogram import Bot

from ... import database as db
from ...functions.parser import Parser
from ..utils.logger import logger


async def auto_update(bot: Bot):

    logger.info("Auto-Update of grades/deadlines:")

    parser = Parser()

    for user_id in await db.get_all_users():
        moodle_userid, token = await db.get_user_data(user_id)
        
        courses_dict = await parser.get_courses(token, moodle_userid)
        if courses_dict is None:
            return
        grades_dict = json.loads(await db.get_key(user_id, 'grades'))
        deadlines_dict = json.loads(await db.get_key(user_id, 'deadlines'))

        new_grades_dict = {}
        for id_course in courses_dict.keys():
            new_grades_dict.update({id_course: await parser.get_grades(id_course, token, moodle_userid)})
            if new_grades_dict[id_course] is None:
                return
        new_deadlines_dict = await parser.get_deadlines(token, courses_dict)
        if new_deadlines_dict is None:
            return

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
            logger.info(f"{user_id} - grades - true")
        else:
            logger.info(f"{user_id} - grades - false")
        if isNewDeadline:
            await bot.send_message(chat_id=user_id, text=text_deadlines, parse_mode='HTML')
            logger.info(f"{user_id} - deadlines - true")
        else:
            logger.info(f"{user_id} - deadlines - false")

        await db.set_keys(user_id, {
            'courses': json.dumps(courses_dict),
            'grades': json.dumps(new_grades_dict),
            'deadlines': json.dumps(new_deadlines_dict)
        })


def register_schedulers(bot, scheduler):
    now = datetime.datetime.now()
    time_start = (now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=10 - now.minute % 10)).strftime(
        "%Y-%m-%d %H:%M:%S")
    scheduler.add_job(auto_update, 'interval', minutes=10, start_date=time_start, kwargs={'bot': bot})
