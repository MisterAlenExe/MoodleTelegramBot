from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import Database
from tgbot.utils.logger import logger, print_msg
from tgbot.utils.throttling import rate_limit
from tgbot.keyboards.moodle import add_delete_button

from functions.login import auth_microsoft, is_cookies_valid
from functions.parser import Parser


class RegForm(StatesGroup):
    waiting_for_barcode = State()
    waiting_for_password = State()


@print_msg
@rate_limit(limit=3)
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
        cookies = await auth_microsoft(barcode, password)
        if await is_cookies_valid(cookies):
            db = Database()
            parser = Parser()
            token, userid = await parser.get_token_and_userid(cookies)
            await db.register_moodle_user(message.from_user.id, barcode, password, cookies, userid, token)
            await message.answer("Your Moodle account is registred\!", parse_mode='MarkdownV2',
                                 reply_markup=add_delete_button())
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


def register_form(dp: Dispatcher):
    dp.register_message_handler(register_moodle, commands=['register'])
    dp.register_message_handler(wait_barcode, content_types=['text'], state=RegForm.waiting_for_barcode)
    dp.register_message_handler(wait_password, content_types=['text'], state=RegForm.waiting_for_password)
