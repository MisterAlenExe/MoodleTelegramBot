import json
import datetime

from aiogram import Dispatcher, types

from database import Database, decrypt
from functions.login import is_cookies_valid, auth_microsoft
from functions.parser import Parser

from tgbot.keyboards.moodle import add_delete_button, courses_btns
from tgbot.keyboards.grades import back_to_grades_courses
from tgbot.utils.logger import logger, print_msg
from tgbot.utils.throttling import rate_limit


async def grades(call: types.CallbackQuery):
    db = Database()
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    await call.message.edit_text("Choose course:", reply_markup=courses_btns('grades', courses_dict))


async def show_grades_for_course(call: types.CallbackQuery):
    db = Database()
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    grades_dict = json.loads(await db.get_key(call.from_user.id, 'grades'))

    id_course = call.data.split()[1]

    text = f"<a href=\"{courses_dict[id_course]['link']}\">{courses_dict[id_course]['name']}</a>:\n"
    for itemname, grade in grades_dict[id_course].items():
        text += f"  {itemname} - {grade}\n"

    await call.message.edit_text(text, reply_markup=back_to_grades_courses(), parse_mode='HTML')
    await call.answer()


def register_grades(dp: Dispatcher):
    dp.register_callback_query_handler(
        grades,
        lambda c: c.data == 'grades'
    )
    dp.register_callback_query_handler(
        show_grades_for_course,
        lambda c: c.data.split()[0] == 'grades',
        lambda c: c.data.split()[1].isdigit()
    )
