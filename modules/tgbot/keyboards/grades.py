from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_to_grades_courses(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('Back', callback_data='grades')
    kb.add(back_btn)

    return kb
