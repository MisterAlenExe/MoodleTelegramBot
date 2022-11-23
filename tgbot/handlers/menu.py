from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from tgbot.handlers.logger import logger, print_msg

from parser import Parser
from config import load_config


@print_msg
async def start(message: types.Message):
    text = "Welcome, bro!"
    await message.reply(text)


@print_msg
async def send_grades(message: types.Message):
    args = message.get_args()
    data = load_config()
    parser = Parser()
    text = parser.get_grades(args)
    await message.reply(text)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(send_grades, commands=['grades'])
