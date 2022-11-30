from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from tgbot.utils.logger import logger, print_msg
from tgbot.utils.config import load_config
from tgbot.utils.throttling import rate_limit
from tgbot.keyboards.inline import add_delete_button, add_courses_buttons

from moodle.parser import Parser


@print_msg
@rate_limit(limit=3)
async def start(message: types.Message):
    text = "Welcome, bro!"
    await message.reply(text)


@print_msg
@rate_limit(limit=3)
async def send_active_courses(message: types.Message):
    parser = Parser()
    text = parser.get_courses()
    await message.reply(text, reply_markup=add_delete_button())


@print_msg
@rate_limit(limit=3)
async def send_grades(message: types.Message):
    await message.reply("Choose course:", reply_markup=add_delete_button(add_courses_buttons()))


async def grades(call: types.CallbackQuery):
    parser = Parser()
    if call.data in parser.get_courses().keys():
        text = parser.get_grades(call.data)
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

    dp.register_callback_query_handler(
        grades,
        lambda c: c.data.isdigit()
    )
    dp.register_callback_query_handler(
        delete_message,
        lambda c: c.data == 'delete'
    )
