from aiogram import Dispatcher, types

from ...database import Database

from ..keyboards.menu import add_delete_button, main_menu, back_to_menu_btn
from ..utils.logger import logger, print_msg
from ..utils.throttling import rate_limit


@print_msg
@rate_limit(limit=3)
async def menu(message: types.Message):
    db = Database()
    if not await db.if_user_exists(message.from_user.id):
        await db.add_new_user(message.from_user.id)
    text = "Choose one and click:"
    await message.reply(text, reply_markup=add_delete_button(main_menu()))


async def back_to_menu(call: types.CallbackQuery):
    db = Database()
    if not await db.if_user_exists(call.from_user.id):
        await db.add_new_user(call.from_user.id)
    text = "Choose one and click:"
    await call.message.edit_text(text, reply_markup=add_delete_button(main_menu()))


async def profile(call: types.CallbackQuery):
    db = Database()
    userid, barcode = await db.get_keys(call.from_user.id, ('user_id', 'barcode'))
    text = f"User ID: {userid}\n" \
           f"Barcode: {barcode}"
    await call.message.edit_text(text, reply_markup=back_to_menu_btn())


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
    dp.register_message_handler(menu, commands=['start', 'menu', 'help'])

    dp.register_callback_query_handler(
        back_to_menu,
        lambda c: c.data == 'main_menu'
    )
    dp.register_callback_query_handler(
        profile,
        lambda c: c.data == 'profile'
    )
