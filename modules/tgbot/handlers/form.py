from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from ... import database as db
from ..utils.logger import print_msg
from ..utils.throttling import rate_limit
from ..keyboards.moodle import add_delete_button

from ...functions.parser import Parser


class RegForm(StatesGroup):
    waiting_for_barcode = State()
    waiting_for_token = State()


@print_msg
@rate_limit(limit=3)
async def register_moodle(message: types.Message, state: FSMContext):
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
        msg = await message.answer("Write your *token*:", parse_mode='MarkdownV2')
        await RegForm.waiting_for_token.set()

    async with state.proxy() as data:
        data['barcode'] = barcode
        data['msg_del'] = msg


async def wait_token(message: types.Message, state: FSMContext):
    token = message.text
    async with state.proxy() as data:
        await delete_msg(data['msg_del'], message)

    if len(token.split()) > 1:
        msg = await message.answer('Error\! Write your *token* one more time:', parse_mode='MarkdownV2')
        async with state.proxy() as data:
            data['msg_del'] = msg
    else:
        msg = await message.answer("Wait! We are trying to login...")
        async with state.proxy() as data:
            barcode = data['barcode']
            data['msg_del'] = msg
            parser = Parser()
        moodle_userid = await parser.get_user_id(token)
        if moodle_userid is None:
            await message.answer("Error\! Your *token* is invalid\!", parse_mode='MarkdownV2')
            await state.finish()
            return
        await db.register_moodle_user(message.from_user.id, barcode, moodle_userid, token)
        await message.answer("Your Moodle account is registred\!", parse_mode='MarkdownV2',
                                reply_markup=add_delete_button())
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
    dp.register_message_handler(wait_token, content_types=['text'], state=RegForm.waiting_for_token)
