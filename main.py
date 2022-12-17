import asyncio

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.database import Database
from modules.tgbot.utils.config import load_config

from modules.tgbot.handlers.menu import register_menu
from modules.tgbot.handlers.moodle import register_moodle
from modules.tgbot.handlers.grades import register_grades
from modules.tgbot.handlers.deadlines import register_deadlines
from modules.tgbot.handlers.form import register_form
from modules.tgbot.handlers.notify import register_schedulers
from modules.tgbot.utils.logger import logger
from modules.tgbot.middlewares.throttling import ThrottlingMiddleware


def register_all_middlewares(dp):
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_handlers(dp, bot, scheduler):
    register_menu(dp)
    register_moodle(dp)
    register_grades(dp)
    register_deadlines(dp)
    register_form(dp)
    register_schedulers(bot, scheduler)


async def main():
    data_config = load_config()

    logger.info("Starting bot")

    bot = Bot(token=data_config['bot_token'])
    dp = Dispatcher(bot, storage=MemoryStorage())
    scheduler = AsyncIOScheduler(timezone="Asia/Almaty")

    register_all_middlewares(dp)
    register_all_handlers(dp, bot, scheduler)

    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        db = Database()
        await db.close()
        session = bot.get_session()
        session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
