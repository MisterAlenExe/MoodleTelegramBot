import json
import datetime

from aiogram import Dispatcher, types

from ... import database as db
from ...functions.login import is_cookies_valid, auth_microsoft
from ...functions.parser import Parser

from ..keyboards.moodle import add_delete_button
from ..utils.logger import logger, print_msg
from ..utils.throttling import rate_limit


@print_msg
@rate_limit(limit=3)
async def update_data(message: types.Message):
    parser = Parser()

    cookies = json.loads(await db.get_key(message.from_user.id, 'cookies'))
    while not await is_cookies_valid(cookies):
        barcode, password = await db.get_user_data(message.from_user.id)
        cookies = await auth_microsoft(barcode, password)

    token, userid = await db.get_keys(message.from_user.id, 'webservice_token', 'moodle_userid')
    token = db.decrypt(token, userid)

    courses_dict = await parser.get_courses(token, userid)

    grades_dict = {}

    for id_course in courses_dict.keys():
        grades_dict.update({
            str(id_course): await parser.get_grades(id_course, token, userid)
        })

    deadlines = await parser.get_deadlines(token)

    await db.set_keys(
        message.from_user.id,
        {
            'cookies': json.dumps(cookies),
            'courses': json.dumps(courses_dict),
            'grades': json.dumps(grades_dict),
            'deadlines': json.dumps(deadlines)
        }
    )
    await message.reply("Your courses and grades are updated.")


@print_msg
@rate_limit(limit=3)
async def send_active_courses(message: types.Message):
    text = ""
    courses_dict = json.loads(await db.get_key(message.from_user.id, 'courses'))
    for course in courses_dict.values():
        text += f"ID - {course['id']}\n" \
                f"Name - {course['name']}\n" \
                f"Link - {course['link']}\n\n"
    await message.reply(text, reply_markup=add_delete_button())


@print_msg
@rate_limit(limit=3)
async def send_deadlines(message: types.Message):
    courses_dict = json.loads(await db.get_key(message.from_user.id, 'courses'))
    deadlines_dict = json.loads(await db.get_key(message.from_user.id, 'deadlines'))

    text = ""
    time_now = datetime.datetime.now().replace(microsecond=0)

    for id_course, assigns_dict in deadlines_dict.items():
        if assigns_dict:
            link_course = courses_dict[id_course]['link']
            name_course = courses_dict[id_course]['name']
            text += f"<a href=\"{link_course}\">{name_course}</a>:\n"
            for id_assign, assign in assigns_dict.items():
                name_assign = assign['name']
                duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
                deadline = duedate.strftime("%A, %d %B, %I:%M %p")
                remaining = duedate - time_now
                link_assign = assign['link']

                text += f"  <a href=\"{link_assign}\">{name_assign}</a>\n"
                text += f"  {deadline}\n"
                text += f"  Remaining: {remaining}\n\n"

    await message.reply(text, reply_markup=add_delete_button(), parse_mode='HTML')


async def delete_message(call: types.CallbackQuery):
    try:
        await call.bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.message.reply_to_message:
            await call.bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        await call.answer()
    except Exception as error:
        logger.error(error)
        await call.answer("Error")


def register_moodle(dp: Dispatcher):
    dp.register_message_handler(send_deadlines, commands=['deadlines'])
    dp.register_message_handler(send_active_courses, commands=['courses'])
    dp.register_message_handler(update_data, commands=['update_data'])

    dp.register_callback_query_handler(
        delete_message,
        lambda c: c.data == 'delete'
    )
