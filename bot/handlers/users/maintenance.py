from aiogram import Router
from aiogram.types import Message

from bot.filters.maintenance import MaintenanceFilter

maintenance_router = Router()
maintenance_router.message.filter(MaintenanceFilter())
maintenance_router.callback_query.filter(MaintenanceFilter())


@maintenance_router.message()
async def maintenance_mode(message: Message):
    await message.reply(f'Bot is in maintenance mode right now!')
