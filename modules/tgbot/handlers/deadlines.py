import datetime
import json

from aiogram import Dispatcher, types

from ..keyboards.deadlines import deadlines_options, deadlines_day_filters_btns, back_to_deadlines_filters, \
    back_to_deadlines_courses
from ..keyboards.moodle import courses_btns
from ... import database as db


async def deadlines_choose_option(call: types.CallbackQuery):
    await call.message.edit_text("Choose option:", reply_markup=deadlines_options())
    await call.answer()


async def deadlines_option_day_filters(call: types.CallbackQuery):
    await call.message.edit_text("Choose filter:", reply_markup=deadlines_day_filters_btns())


async def deadlines_option_courses(call: types.CallbackQuery):
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    await call.message.edit_text("Choose course:", reply_markup=courses_btns('deadlines', courses_dict))


async def show_deadlines_for_day(call: types.CallbackQuery):
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    deadlines_dict = json.loads(await db.get_key(call.from_user.id, 'deadlines'))

    filter_day = call.data.split()[1]

    text = ""
    time_now = datetime.datetime.now().replace(microsecond=0)
    if filter_day.isdigit():
        filter_time = time_now + datetime.timedelta(days=int(filter_day))
    else:
        filter_time = None

    for id_course, assigns_dict in deadlines_dict.items():
        link_course = courses_dict[id_course]['link']
        name_course = courses_dict[id_course]['name']
        deadline_info = {}
        if filter_day.isdigit():
            if assigns_dict:
                deadline_info = {}
                link_course = courses_dict[id_course]['link']
                name_course = courses_dict[id_course]['name']
                for id_assign, assign in assigns_dict.items():
                    duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
                    if duedate > time_now:
                        if filter_time > duedate:
                            name_assign = assign['name']
                            duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
                            deadline = duedate.strftime("%A, %d %B, %I:%M %p")
                            remaining = duedate - time_now
                            link_assign = assign['link']
                            deadline_info.update({
                                id_assign: {
                                    'name': name_assign,
                                    'link': link_assign,
                                    'deadline': deadline,
                                    'remaining': remaining
                                }
                            })
        else:
            if assigns_dict:
                for id_assign, assign in assigns_dict.items():
                    duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
                    if duedate > time_now:
                        name_assign = assign['name']
                        duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
                        deadline = duedate.strftime("%A, %d %B, %I:%M %p")
                        remaining = duedate - time_now
                        link_assign = assign['link']
                        deadline_info.update({
                            id_assign: {
                                'name': name_assign,
                                'link': link_assign,
                                'deadline': deadline,
                                'remaining': remaining
                            }
                        })
        if len(deadline_info) > 0:
            text += f"<a href=\"{link_course}\">{name_course}</a>:\n"
            for assign in deadline_info.values():
                text += f"  <a href=\"{assign['link']}\">{assign['name']}</a>\n"
                text += f"  {assign['deadline']}\n"
                text += f"  Remaining: {assign['remaining']}\n\n"

    if text == "":
        text = "There are no any deadlines."
        await call.message.edit_text(text, reply_markup=back_to_deadlines_filters(), parse_mode='HTML')
    else:
        await call.message.edit_text(text, reply_markup=back_to_deadlines_filters(), parse_mode='HTML')


async def show_deadlines_for_course(call: types.CallbackQuery):
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    deadlines_dict = json.loads(await db.get_key(call.from_user.id, 'deadlines'))

    id_course = call.data.split()[1]
    text = f"<a href=\"{courses_dict[id_course]['link']}\">{courses_dict[id_course]['name']}</a>:\n"
    time_now = datetime.datetime.now().replace(microsecond=0)
    is_deadline = False

    for _, assign in deadlines_dict[id_course].items():
        name_assign = assign['name']
        duedate = datetime.datetime.fromtimestamp(assign['deadline']).replace(microsecond=0)
        deadline = duedate.strftime("%A, %d %B, %I:%M %p")
        remaining = duedate - time_now
        link_assign = assign['link']

        text += f"  <a href=\"{link_assign}\">{name_assign}</a>\n"
        text += f"  {deadline}\n"
        text += f"  Remaining: {remaining}\n\n"

        is_deadline = True
    if not is_deadline:
        text = "There are no any deadlines."

    await call.message.edit_text(text, reply_markup=back_to_deadlines_courses(), parse_mode='HTML')
    await call.answer()


def register_deadlines(dp: Dispatcher):
    dp.register_callback_query_handler(
        deadlines_choose_option,
        lambda c: c.data.split()[0] == 'deadlines',
        lambda c: c.data.split()[1] == 'options'
    )
    dp.register_callback_query_handler(
        deadlines_option_day_filters,
        lambda c: c.data.split()[0] == 'deadlines',
        lambda c: c.data.split()[1] == 'days'
    )
    dp.register_callback_query_handler(
        deadlines_option_courses,
        lambda c: c.data.split()[0] == 'deadlines',
        lambda c: c.data.split()[1] == 'courses'
    )
    dp.register_callback_query_handler(
        show_deadlines_for_day,
        lambda c: c.data.split()[0] == 'day',
        lambda c: c.data.split()[1].isdigit() or c.data.split()[1] == 'all'
    )
    dp.register_callback_query_handler(
        show_deadlines_for_course,
        lambda c: c.data.split()[0] == 'deadlines',
        lambda c: c.data.split()[1].isdigit()
    )
