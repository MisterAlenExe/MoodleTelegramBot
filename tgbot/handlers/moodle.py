import json

from aiogram import Dispatcher, types

from database import Database, crypt, decrypt
from tgbot.utils.logger import logger, print_msg
from tgbot.utils.throttling import rate_limit
from tgbot.keyboards.inline import add_delete_button, add_courses_buttons, add_back_button

from moodle.parser import Parser


@print_msg
@rate_limit(limit=3)
async def update_data(message: types.Message):
    db = Database()
    barcode, password = await db.get_user_data(message.from_user.id)
    parser = Parser(barcode, password)
    cookies = parser.get_cookies()
    courses_dict = parser.get_courses(cookies)
    token, userid = parser.get_token_and_userid(cookies)
    grades_dict = {}
    for id_course in courses_dict.keys():
        grades_dict.update({
            id_course: parser.get_grades(id_course, token, userid)
        })
    await db.set_keys(
        message.from_user.id,
        {
            'userid': userid,
            'webservice_token': crypt(token, userid),
            'cookies': json.dumps(cookies),
            'courses': json.dumps(courses_dict),
            'grades': json.dumps(grades_dict)
        }
    )
    await message.reply("Your courses and grades are updated.")


@print_msg
@rate_limit(limit=3)
async def send_active_courses(message: types.Message):
    text = ""
    db = Database()
    courses_dict = json.loads(await db.get_key(message.from_user.id, 'courses'))
    for course in courses_dict.values():
        text += f"ID - {course['id']}\n" \
                f"Name - {course['name']}\n" \
                f"Link - {course['link']}\n\n"
    await message.reply(text, reply_markup=add_delete_button())


@print_msg
@rate_limit(limit=3)
async def send_grades(message: types.Message):
    db = Database()
    courses_dict = json.loads(await db.get_key(message.from_user.id, 'courses'))
    await message.reply("Choose course:", reply_markup=add_delete_button(add_courses_buttons(courses_dict)))


async def grades(call: types.CallbackQuery):
    db = Database()
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    if call.data in courses_dict.keys():
        text = ""
        grades_dict = json.loads(await db.get_key(call.from_user.id, 'grades'))
        for itemname, grade in grades_dict[call.data].items():
            text += f"{itemname} - {grade}\n"
        await call.message.edit_text(text, reply_markup=add_back_button())
    elif call.data == 'back_to_courses':
        await call.message.edit_text("Choose course:", reply_markup=add_delete_button(add_courses_buttons(
            courses_dict)))
    await call.answer()


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
    dp.register_message_handler(send_grades, commands=['grades'])
    dp.register_message_handler(send_active_courses, commands=['courses'])
    dp.register_message_handler(update_data, commands=['update_data'])

    dp.register_callback_query_handler(
        grades,
        lambda c: c.data.isdigit() or c.data == 'back_to_courses'
    )
    dp.register_callback_query_handler(
        delete_message,
        lambda c: c.data == 'delete'
    )
