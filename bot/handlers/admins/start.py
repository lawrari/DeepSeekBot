from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.filters.admin import AdminFilter
from config.config import Config

admin_start_router = Router()
admin_start_router.message.filter(AdminFilter())


@admin_start_router.message(CommandStart())
async def start_handler(message: Message):
    await message.reply(f'Hello, {message.from_user.full_name}! You are admin!')


@admin_start_router.message(Command('maintenance'))
async def toggle_maintenance(message: Message, config: Config):
    config.misc.bot_maintenance = not config.misc.bot_maintenance
    await message.reply(f'Bot maintenance mode is now {config.misc.bot_maintenance}')
