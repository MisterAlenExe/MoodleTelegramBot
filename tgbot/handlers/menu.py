import json

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import Database
from tgbot.utils.logger import logger, print_msg
from tgbot.utils.config import load_config
from tgbot.utils.throttling import rate_limit
from tgbot.keyboards.inline import add_delete_button, add_courses_buttons, add_back_button

from moodle.login import auth_microsoft
from moodle.parser import Parser


class RegForm(StatesGroup):
    waiting_for_barcode = State()
    waiting_for_password = State()


@print_msg
@rate_limit(limit=3)
async def start(message: types.Message):
    db = Database()
    if await db.if_user_exists(message.from_user.id):
        text = "Hello! I know you."
    else:
        await db.add_new_user(message.from_user.id)
        text = "Hello! Who are you?"
    await message.reply(text)


@print_msg
@rate_limit(limit=3)
async def update_data(message: types.Message):
    db = Database()
    barcode, password = await db.get_user_data(message.from_user.id)
    parser = Parser(barcode, password)
    courses_dict = parser.get_courses()
    grades_dict = {}
    for id_course in courses_dict.keys():
        grades_dict.update({
            id_course: parser.get_grades(id_course)
        })
    await db.set_key(message.from_user.id, 'courses', json.dumps(courses_dict))
    await db.set_key(message.from_user.id, 'grades', json.dumps(grades_dict))
    await message.reply("Your courses and grades are updated.")


@print_msg
@rate_limit(limit=3)
async def send_active_courses(message: types.Message):
    text = ""
    db = Database()
    courses_dict = json.loads(await db.get_key(message.from_user.id, 'courses'))
    for course in courses_dict.values():
        text += f"ID - {course['id']}\n" \
                f"Name - {course['name']}\n" \
                f"Link - {course['link']}\n\n"
    await message.reply(text, reply_markup=add_delete_button())


@print_msg
@rate_limit(limit=3)
async def send_grades(message: types.Message):
    db = Database()
    courses_dict = json.loads(await db.get_key(message.from_user.id, 'courses'))
    await message.reply("Choose course:", reply_markup=add_delete_button(add_courses_buttons(courses_dict)))


async def grades(call: types.CallbackQuery):
    db = Database()
    courses_dict = json.loads(await db.get_key(call.from_user.id, 'courses'))
    if call.data in courses_dict.keys():
        text = ""
        grades_dict = json.loads(await db.get_key(call.from_user.id, 'grades'))
        for itemname, grade in grades_dict[call.data].items():
            text += f"{itemname} - {grade}\n"
        await call.message.edit_text(text, reply_markup=add_back_button())
    elif call.data == 'back_to_courses':
        await call.message.edit_text("Choose course:", reply_markup=add_delete_button(add_courses_buttons(
            courses_dict)))
    await call.answer()


async def register_moodle(message: types.Message, state: FSMContext):
    db = Database()
    if not await db.if_user_exists(message.from_user.id):
        await db.add_new_user(message.from_user.id)

    msg = await message.answer("Write your *barcode*:", parse_mode='MarkdownV2')
    await delete_msg(message)
    await RegForm.waiting_for_barcode.set()

    async with state.proxy() as data:
        data['msg_del'] = msg


async def wait_barcode(message: types.Message, state: FSMContext):
    barcode = message.text
    async with state.proxy() as data:
        await delete_msg(data['msg_del'], message)

    if not barcode.isdigit():
        msg = await message.answer('Error\! Write your *barcode* one more time:', parse_mode='MarkdownV2')
    else:
        msg = await message.answer("Write your *password*:", parse_mode='MarkdownV2')
        await RegForm.waiting_for_password.set()

    async with state.proxy() as data:
        data['barcode'] = barcode
        data['msg_del'] = msg


async def wait_password(message: types.Message, state: FSMContext):
    password = message.text
    async with state.proxy() as data:
        await delete_msg(data['msg_del'], message)

    if len(password.split()) > 1:
        msg = await message.answer('Error\! Write your *password* one more time:', parse_mode='MarkdownV2')
        async with state.proxy() as data:
            data['msg_del'] = msg
    else:
        msg = await message.answer("Wait! We are trying to login...")
        async with state.proxy() as data:
            barcode = data['barcode']
            data['msg_del'] = msg
        if auth_microsoft(barcode, password):
            db = Database()
            await db.register_moodle_user(message.from_user.id, barcode, password)
            await message.answer("Your Moodle account is registred\!", parse_mode='MarkdownV2', reply_markup=add_delete_button())
        else:
            await message.answer("Your barcode or password are invalid. Try again!", reply_markup=add_delete_button())
        async with state.proxy() as data:
            await delete_msg(data['msg_del'])
        await state.finish()


async def delete_msg(*msgs: types.Message):
    msgs = reversed(msgs)
    for msg in msgs:
        try:
            await msg.delete()
        except:
            pass


async def delete_message(call: types.CallbackQuery):
    try:
        await call.bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.message.reply_to_message:
            await call.bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        await call.answer()
    except Exception as error:
        logger.error(error)
        await call.answer("Error")


def register_menu(dp: Dispatcher):
    dp.register_message_handler(register_moodle, commands=['register'])
    dp.register_message_handler(wait_barcode, content_types=['text'], state=RegForm.waiting_for_barcode)
    dp.register_message_handler(wait_password, content_types=['text'], state=RegForm.waiting_for_password)
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(send_grades, commands=['grades'])
    dp.register_message_handler(send_active_courses, commands=['courses'])
    dp.register_message_handler(update_data, commands=['update_data'])

    dp.register_callback_query_handler(
        grades,
        lambda c: c.data.isdigit() or c.data == 'back_to_courses'
    )
    dp.register_callback_query_handler(
        delete_message,
        lambda c: c.data == 'delete'
    )
