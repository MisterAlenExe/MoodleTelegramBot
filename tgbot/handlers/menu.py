import json
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from database import Database
from tgbot.utils.logger import logger, print_msg
from tgbot.utils.config import load_config
from tgbot.utils.throttling import rate_limit
from tgbot.keyboards.inline import add_delete_button, add_courses_buttons

from moodle.parser import Parser


@print_msg
@rate_limit(limit=3)
async def start(message: types.Message):
    db = Database()
    if await db.if_user_exists(message.from_user.id):
        text = "Hello! I know you."
    else:
        await db.add_new_user(message.from_user.id)
        text = "Hello! Who are you?"
    await message.reply(text)


@print_msg
@rate_limit(limit=3)
async def new_user(message: types.Message):
    db = Database()
    user_id = '123123'
    grades = {
        "Discrete Math": "85",
        "Foreign Language": "90",
        "Psychology": "93"
    }
    courses = {
        "1234": "Discrete Math",
        "4567": "Foreign Language",
        "9567": "Psychology"
    }
    new_user = {
        "user_id": user_id,
        "grades": json.dumps(grades),
        "courses": json.dumps(courses)
    }
    # await db.set_keys(user_id, new_user)
    # text = await db.get_keys(user_id, ["grades", "courses"])
    text = await db.get_dict(user_id)
    await message.reply(text)


@print_msg
@rate_limit(limit=3)
async def send_active_courses(message: types.Message):
    parser = Parser()
    courses = parser.get_courses()
    text = ""
    db = Database()
    await db.set_key(message.from_user.id, 'courses', json.dumps(courses))
    for _, el in courses.items():
        text += f"ID - {el['id']}\n" \
                f"Name - {el['name']}\n" \
                f"Link - {el['link']}\n\n"
    await message.reply(text, reply_markup=add_delete_button())


@print_msg
@rate_limit(limit=3)
async def send_grades(message: types.Message):
    await message.reply("Choose course:", reply_markup=add_delete_button(add_courses_buttons()))


async def grades(call: types.CallbackQuery):
    parser = Parser()
    if call.data in parser.get_courses().keys():
        marks = parser.get_grades(call.data)
        text = ""
        for itemname, grade in marks.items():
            text += f"{itemname} - {grade}\n"
        await call.message.edit_text(text, reply_markup=add_delete_button())
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


def register_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(send_grades, commands=['grades'])
    dp.register_message_handler(send_active_courses, commands=['courses'])
    dp.register_message_handler(new_user, commands=['test'])

    dp.register_callback_query_handler(
        grades,
        lambda c: c.data.isdigit()
    )
    dp.register_callback_query_handler(
        delete_message,
        lambda c: c.data == 'delete'
    )
