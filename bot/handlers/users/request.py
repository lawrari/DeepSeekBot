from aiogram import Router
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from aiogram import F

import asyncio

from services.apis.DeepSeek.dialogs import Dialog
from services.apis.DeepSeek.deepseek import DeepSeek
from services.apis.DeepSeek.formatting import Formattor
from services.apis.yandex_api import YandexOCR
from services.database.repo.requests import RequestsRepo

request_router = Router()


@request_router.message(Command("reset"))
async def reset_context(message: Message, dialog: Dialog):
    await dialog.clear()
    await message.answer("Контекст очищен")

@request_router.message(F.photo)
async def image_request(message: Message, dialog: Dialog, ai_client: DeepSeek, yandex_client: YandexOCR):
    pass

# TODO: accept images, all other files, reset context, fault-proof
@request_router.message()
async def text_request(message: Message, dialog: Dialog, ai_client: DeepSeek, repo: RequestsRepo):
    if len(dialog) > 0 and dialog[-1]['role'] == 'user':
        await message.answer("Дождитесь ответа на предыдущее сообщение")
        return

    user_request = message.text

    await dialog.add_user_message(user_request)
    print(dialog.messages)

    content = []
    response_message = await message.answer("Отправка запроса...")
    async for chunk in ai_client.stream_response(dialog):
        content += chunk[0]
        try:
            await response_message.edit_text(Formattor.format_text(content)[0], parse_mode="MarkdownV2")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(e)

    final_text_with_files = Formattor.format_text("".join(content))

    if not final_text_with_files[0]:
        await response_message.edit_text("Ошибка на серверах DeepSek, попробуйте позже")
        dialog.messages.pop()
    else:
        if final_text_with_files[1]:
            for file in final_text_with_files[1]:
                document = BufferedInputFile(file[1], filename=file[0])
                await message.answer_document(document)

        
        await dialog.add_assistant_message("".join(content))
