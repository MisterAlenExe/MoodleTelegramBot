from aiogram import Dispatcher, types

from database import Database
from tgbot.utils.logger import logger, print_msg
from tgbot.utils.throttling import rate_limit


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
