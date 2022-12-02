from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_delete_button(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton("Delete", callback_data="delete")
    kb.add(del_btn)
    return kb


def add_courses_buttons(courses_dict: dict):
    kb = InlineKeyboardMarkup()
    for course in courses_dict.values():
        course_btn = InlineKeyboardButton(course['name'], callback_data=course['id'])
        kb.add(course_btn)
    return kb


def add_back_button():
    kb = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton("Back", callback_data="back_to_courses")
    kb.add(back_btn)
    return kb
