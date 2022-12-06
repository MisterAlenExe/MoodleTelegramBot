from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_delete_button(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton('Delete', callback_data='delete')
    kb.add(del_btn)

    return kb


def grades_courses_btns(courses_dict: dict, kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    index = 1
    for course in courses_dict.values():
        course_btn = InlineKeyboardButton(course['name'], callback_data=course['id'])
        if index % 2 != 1:
            kb.insert(course_btn)
        else:
            kb.add(course_btn)
        index += 1
    back_btn = InlineKeyboardButton('Back', callback_data='main_menu')
    kb.add(back_btn)

    return kb


def back_to_grades(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('Back', callback_data='grades')
    kb.add(back_btn)

    return kb
