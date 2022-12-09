from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_delete_button(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton('Delete', callback_data='delete')
    kb.add(del_btn)

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
