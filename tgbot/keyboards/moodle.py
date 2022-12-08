from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_delete_button(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton('Delete', callback_data='delete')
    kb.add(del_btn)

    return kb


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
    one_day = InlineKeyboardButton('<1 day', callback_data='1 day')
    two_day = InlineKeyboardButton('<2 days', callback_data='2 day')
    five_day = InlineKeyboardButton('<5 day', callback_data='5 day')
    ten_day = InlineKeyboardButton('<10 day', callback_data='10 day')
    fifteen_day = InlineKeyboardButton('<15 day', callback_data='15 day')
    all_day = InlineKeyboardButton('All', callback_data='all day')
    kb.row(one_day, two_day)
    kb.row(five_day, ten_day)
    kb.row(fifteen_day, all_day)
    back_btn = InlineKeyboardButton('Back', callback_data='deadlines options')
    kb.add(back_btn)

    return kb


def courses_btns(flag, courses_dict: dict, kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    index = 1
    for course in courses_dict.values():
        course_btn = InlineKeyboardButton(course['name'], callback_data=f"{flag} {course['id']}")
        if index % 2 != 1:
            kb.insert(course_btn)
        else:
            kb.add(course_btn)
        index += 1
    if flag == 'grades':
        back_btn = InlineKeyboardButton('Back', callback_data='main_menu')
    else:
        back_btn = InlineKeyboardButton('Back', callback_data='deadlines options')
    kb.add(back_btn)

    return kb


def back_to_grades_courses(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('Back', callback_data='grades')
    kb.add(back_btn)

    return kb


def back_to_deadlines_courses(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('Back', callback_data='deadlines courses')
    kb.add(back_btn)

    return kb
