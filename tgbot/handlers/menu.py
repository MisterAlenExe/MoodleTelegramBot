from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from tgbot.utils.logger import logger, print_msg
from tgbot.utils.config import load_config
from tgbot.utils.throttling import rate_limit

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
    # await message.reply(text)


@print_msg
@rate_limit(limit=3)
async def send_grades(message: types.Message):
    args = message.get_args()
    parser = Parser()
    text = parser.get_grades(args)
    # await message.reply(text)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(send_grades, commands=['grades'])
    dp.register_message_handler(send_active_courses, commands=['courses'])
