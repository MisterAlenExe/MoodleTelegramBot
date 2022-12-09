from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def deadlines_options(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    course_btn = InlineKeyboardButton('By course filter', callback_data='deadlines courses')
    day_btn = InlineKeyboardButton('By day filter', callback_data='deadlines days')
    back_btn = InlineKeyboardButton('Back', callback_data='main_menu')
    kb.row(course_btn, day_btn)
    kb.add(back_btn)

    return kb


def deadlines_day_filters_btns(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    one_day = InlineKeyboardButton('<1 day', callback_data='day 1')
    two_day = InlineKeyboardButton('<2 days', callback_data='day 2')
    five_day = InlineKeyboardButton('<5 day', callback_data='day 5')
    ten_day = InlineKeyboardButton('<10 day', callback_data='day 10')
    fifteen_day = InlineKeyboardButton('<15 day', callback_data='day 15')
    all_day = InlineKeyboardButton('All', callback_data='day all')
    kb.row(one_day, two_day)
    kb.row(five_day, ten_day)
    kb.row(fifteen_day, all_day)
    back_btn = InlineKeyboardButton('Back', callback_data='deadlines options')
    kb.add(back_btn)

    return kb


def back_to_deadlines_courses(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('Back', callback_data='deadlines courses')
    kb.add(back_btn)

    return kb


def back_to_deadlines_filters(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('Back', callback_data='deadlines days')
    kb.add(back_btn)

    return kb
