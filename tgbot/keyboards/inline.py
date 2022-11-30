from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from moodle.parser import Parser


def add_delete_button(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton("Delete", callback_data="delete")
    kb.add(del_btn)
    return kb


def add_courses_buttons():
    kb = InlineKeyboardMarkup()
    parser = Parser()
    courses = parser.get_courses()
    for id_subject, name_subject in courses.items():
        course_btn = InlineKeyboardButton(name_subject, callback_data=id_subject)
        kb.add(course_btn)
    return kb
