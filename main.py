import asyncio

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.utils.config import load_config

from tgbot.handlers.menu import register_menu
from tgbot.utils.logger import logger
from tgbot.middlewares.throttling import ThrottlingMiddleware


async def main():
    data_config = load_config()
    # parser = Parser()
    # parser.get_courses()
    # parser.get_grades()

    logger.info("Starting bot")

    bot = Bot(token=data_config['bot_token'])
    dp = Dispatcher(bot, storage=MemoryStorage())

    dp.setup_middleware(ThrottlingMiddleware())
    register_menu(dp)

    await dp.start_polling()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
