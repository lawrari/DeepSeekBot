from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload

from services.database.models.users import User
from services.database.repo.requests import RequestsRepo
from bot.keyboards.main_menu import get_main_menu_keyboard


user_start_router = Router()
referral_start_router = Router()

# EXAMPLE USAGE OF USAGE
#
# @user_start_router.message(Command("use"))
# async def use(message: Message, repo: RequestsRepo, profile: Profile):
#     profile_id = profile.profile_id
#     request_type = random.choice(["Text", "Image"])
#     input_tokens_used = random.randint(100, 10000)
#     output_tokens_used = random.randint(100, 10000)
#     yandex_input_tokens_used = random.randint(100, 10000) if request_type == "Image" else 0
#     yandex_output_tokens_used = random.randint(100, 10000) if request_type == "Image" else 0
#     seconds_spent_on_request = random.randint(1, 30)

#     usage = await repo.usages.add_usage(
#         profile_id, 
#         request_type, 
#         input_tokens_used, 
#         output_tokens_used,
#         yandex_input_tokens_used,
#         yandex_output_tokens_used,
#         seconds_spent_on_request
#         )


# @referral_start_router.message(CommandStart(deep_link=True))
# async def referral_handler(message: Message, command: CommandObject, repo: RequestsRepo):
#     args = command.args
#     invitor = int(decode_payload(args))
#     invitee = int(message.from_user.id)

#     keyboard = await get_main_menu_keyboard()

#     if await repo.users.user_exists(invitor):
#         if not await repo.users.user_exists(invitee):
#             user = await repo.users.get_or_create_user_and_profile(
#                 telegram_id=message.from_user.id,
#                 username=message.from_user.username,
#                 full_name=message.from_user.full_name,
#                 language=message.from_user.language_code,
#             )

#             await repo.invitations.create_invitation(invitor, invitee)

#             subscription = await repo.subscriptions.get_subscription(2)
#             text_requests = subscription.requests_amount
#             image_requests = subscription.image_requests_amount

#             await repo.profiles.add_requests(user.profile.profile_id, text_requests, image_requests)

#             await message.answer("<b>⭐️ Я — ваш универсальный помощник!\n" \
#                                 f"⚡️ Сейчас у вас {user.profile.text_requests} текстовых запроса и {user.profile.image_requests} запросов с изображением</b>\n\n" \
#                                 "<i>Просто напиши свой вопрос для начала работы!</i>", reply_markup=keyboard, parse_mode="HTML")
#         else:
#             await message.answer("<b>⭐️ Я — ваш универсальный помощник!\n" \
#                                 f"⚡️ Сейчас у вас {user.profile.text_requests} текстовых запроса и {user.profile.image_requests} запросов с изображением</b>\n\n" \
#                                 "<i>Просто напиши свой вопрос для начала работы!</i>", reply_markup=keyboard, parse_mode="HTML")
#     else:
#         user = await repo.users.get_or_create_user_and_profile(
#                 telegram_id=message.from_user.id,
#                 username=message.from_user.username,
#                 full_name=message.from_user.full_name,
#                 language=message.from_user.language_code,
#             )

#         await message.answer("<b>⭐️ Я — ваш универсальный помощник!\n" \
#                             f"⚡️ Сейчас у вас {user.profile.text_requests} текстовых запроса и {user.profile.image_requests} запросов с изображением</b>\n\n" \
#                             "<i>Просто напиши свой вопрос для начала работы!</i>", reply_markup=keyboard, parse_mode="HTML")


@user_start_router.message(CommandStart())
async def start_handler(message: Message, user: User):
    text = (
        "**⭐️ Я — ваш универсальный помощник!**\n"
        "**⚡️ Сейчас у вас ∞ бесплатных запросов**\n\n"
        "Пока что пользоваться мной можно бесплатно и без ограничений, поделись с друзьями!\n\n"
        "*Просто напиши свой вопрос для начала работы!*"
    )
    await message.answer(text)
