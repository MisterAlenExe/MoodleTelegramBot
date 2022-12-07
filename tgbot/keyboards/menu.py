from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_delete_button(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton("Delete", callback_data="delete")
    kb.add(del_btn)

    return kb


def main_menu(kb: types.inline_keyboard = None):
    if kb is None:
        kb = InlineKeyboardMarkup()
    profile_btn = InlineKeyboardButton('Profile', callback_data='profile')
    grades_btn = InlineKeyboardButton('Grades', callback_data='grades')
    deadlines_btn = InlineKeyboardButton('Deadlines', callback_data='deadlines options')
    kb.add(profile_btn)
    kb.row(grades_btn, deadlines_btn)

    return kb
