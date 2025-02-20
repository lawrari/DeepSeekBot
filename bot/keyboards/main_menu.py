from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


async def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Купить запросы", callback_data="buy_requests_start"))
    builder.add(InlineKeyboardButton(text="Пригласить друзей", callback_data="invite_start"))
    builder.add(InlineKeyboardButton(text="Свзаться", url="t.me/aizen_work"))
