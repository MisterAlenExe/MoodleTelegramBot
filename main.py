import asyncio

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from database import Database
from tgbot.utils.config import load_config

from tgbot.handlers.menu import register_menu
from tgbot.handlers.moodle import register_moodle
from tgbot.handlers.form import register_form
from tgbot.handlers.notify import register_schedulers
from tgbot.utils.logger import logger
from tgbot.middlewares.throttling import ThrottlingMiddleware


def register_all_middlewares(dp):
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_handlers(dp):
    register_menu(dp)
    register_moodle(dp)
    register_form(dp)
    register_schedulers(dp)


async def main():
    data_config = load_config()

    logger.info("Starting bot")

    bot = Bot(token=data_config['bot_token'])
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_all_middlewares(dp)
    register_all_handlers(dp)

    await dp.start_polling()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
    finally:
        db = Database()
        asyncio.run(db.close())
