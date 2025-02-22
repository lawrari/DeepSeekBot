from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload

from services.database.models.users import User
from services.database.models.profiles import Profile
from services.database.repo.requests import RequestsRepo
from services.apis.payments.yookassa_helper import YooKassaHelper
from bot.keyboards.main_menu import get_main_menu_keyboard

import random
import uuid


payments_router = Router()


@payments_router.message(Command("pay"))
async def payments_handler(message: Message, user: User, repo: RequestsRepo, yookassa_helper: YooKassaHelper):
    payment_id = uuid.uuid4()
    payment = await yookassa_helper.create_payment(
        telegram_user_id=message.from_user.id,
        amount=random.randint(100, 1000),
        payment_id=payment_id
    )
    db_payment = await repo.payments.create_payment(
        payment_id=payment.id,
        payer_id=user.profile.profile_id,
        amount=payment.amount.value,
        subscription_id=2
    )
    print(f"id of created payment: {payment_id}/{payment.id}, id in database: {db_payment.payment_id}")

    await message.answer(payment.confirmation.confirmation_url)
