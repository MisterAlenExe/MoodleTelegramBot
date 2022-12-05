import datetime
from math import ceil

from aiogram import types

from tgbot.handlers.moodle import update_data


async def notify_user(message: types.Message, text):
    await message.answer(text, parse_mode='HTML')


def register_schedulers(bot, scheduler):
    now = datetime.datetime.now()
    hours, minutes = divmod(ceil(now.minute / 30) * 30, 60)
    rounded_time = (now + datetime.timedelta(hours=hours)).replace(minute=minutes, second=0).strftime(
        "%Y-%m-%d %H:%M:%S")
    scheduler.add_job(update_data, 'interval', minutes=1, start_date=rounded_time)
