import io

from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.chat_action import ChatActionSender

import time

from services.apis.DeepSeek.dialogs import Dialog
from services.apis.DeepSeek.deepseek import DeepSeek
from services.apis.DeepSeek.formatting import Formattor
from services.apis.yandex_api import YandexOCR
from services.database.repo.requests import RequestsRepo

from scripts.file_reader import FilesToText

request_router = Router()


@request_router.message(Command("reset"))
async def reset_context(message: Message, dialog: Dialog):
    await dialog.clear()
    await message.answer("🗑️・История диалога очищена")


@request_router.message(F.photo)
async def image_request(message: Message, dialog: Dialog, ai_client: DeepSeek, yandex_ocr: YandexOCR):
    if message.media_group_id:
        await message.answer("👾・Отправляейте файлы по одному!")
        return
    if len(dialog) > 0 and dialog[-1]['role'] == 'user':
        await message.answer("⏳・Дождитесь ответа на прошлый запрос")
        return

    user_request = message.caption

    image_id = message.photo[-1].file_id
    image_bytes = io.BytesIO()
    image = await message.bot.download(file=image_id, destination=image_bytes)
    base64_image = yandex_ocr.encode_file(image_bytes)
    image_text = await yandex_ocr.recognize(base64_image)

    full_request = f"Текст на изображении: {image_text}. {user_request}" if message.caption else f"Текст на изображении: {image_text}."

    if image_text is None:
        await message.answer("👾・Извините, не удалось распознать текст на изображении")
        return
    
    await dialog.add_user_message(full_request)

    content = []
    response_message = await message.answer("Отправка запроса...")

    last_update_time = time.time()
    accumulated_chunks = []
    
    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        async for chunk in ai_client.stream_response(dialog):
            content += chunk[0]
            accumulated_chunks += chunk[0]
            
            current_time = time.time()
            is_final_chunk = chunk[1] is not None and chunk[1]

            if current_time - last_update_time >= 2 or is_final_chunk:
                try:
                    formatted_text = Formattor.format_text("".join(content))[0]
                    await response_message.edit_text(formatted_text, parse_mode="MarkdownV2")
                    accumulated_chunks = []
                    last_update_time = current_time
                except Exception as e:
                    print(f"Update error: {e}")

    final_text_with_files = Formattor.format_text("".join(content))
    
    if not final_text_with_files[0]:
        await response_message.edit_text("👾・Извините, что-то пошло не так! Попробуйте ещё раз")
        dialog.messages.pop()
    else:
        if final_text_with_files[1]:
            if len(final_text_with_files[1]) > 1:
                media_group = MediaGroupBuilder()
                for file in final_text_with_files[1]:
                    document = BufferedInputFile(file[1], filename=file[0])
                    media_group.add(type='document', media=document)
                await message.answer_media_group(media=media_group.build())
            else:
                document = BufferedInputFile(final_text_with_files[1][1], filename=final_text_with_files[1][0])
                await message.answer_document(document)

        
        await dialog.add_assistant_message("".join(content))


@request_router.message(F.document)
async def document_request(message: Message, dialog: Dialog, ai_client: DeepSeek, yandex_ocr: YandexOCR):
    if message.media_group_id:
        await message.reply("👾・Отправляейте файлы по одному!")
        return
    if len(dialog) > 0 and dialog[-1]['role'] == 'user':
        await message.answer("⏳・Дождитесь ответа на прошлый запрос")
        return

    user_request = message.caption

    file_id = message.document.file_id
    filename = message.document.file_name
    file_bytes = io.BytesIO()
    file = await message.bot.download(file=file_id, destination=file_bytes)

    if filename.endswith('.docx'):
        extracted = FilesToText.extract_docx_content(file)
        extracted_text = extracted['text']
        if extracted['images']:
            extracted_images = extracted['images']
            extracted_images_texts = []
            counter = 1
            for image in extracted_images:
                base64_image = yandex_ocr.encode_file(image)
                image_text = await yandex_ocr.recognize(base64_image)
                if image_text is None:
                    image_text = "отстутствует"
                extracted_images_texts.append(f"Изображение номер {counter}: {image_text}")
        else:
            extracted_images_texts = ['отстутствуют']
        
        full_request = f"Текст в файле: {extracted_text}. Текста на изображенниях: {','.join(extracted_images_texts)}. {user_request}"
        
    elif filename.endswith('.xlsx'):
        extracted = FilesToText.extract_xlsx_content(file)
        extracted_text = extracted['text']
        if extracted['images']:
            extracted_images = extracted['images']
            extracted_images_texts = []
            counter = 1
            for image in extracted_images:
                base64_image = yandex_ocr.encode_file(image)
                image_text = await yandex_ocr.recognize(base64_image)
                if image_text is None:
                    image_text = "отстутствует"
                extracted_images_texts.append(f"Изображение номер {counter}: {image_text}")
        else:
            extracted_images_texts = ['отстутствуют']
        
        full_request = f"Текст в файле: {extracted_text}. Текста на изображенниях: {','.join(extracted_images_texts)}. {user_request}"

    elif filename.endswith('.pptx'):
        extracted = FilesToText.extract_pptx_content(file)
        extracted_text = extracted['text']
        if extracted['images']:
            extracted_images = extracted['images']
            extracted_images_texts = []
            counter = 1
            for image in extracted_images:
                base64_image = yandex_ocr.encode_file(image)
                image_text = await yandex_ocr.recognize(base64_image)
                if image_text is None:
                    image_text = "отстутствует"
                extracted_images_texts.append(f"Изображение номер {counter}: {image_text}")
        else:
            extracted_images_texts = ['отстутствуют']
        
        full_request = f"Текст в файле: {extracted_text}. Текста на изображенниях: {','.join(extracted_images_texts)}. {user_request}"

    else:
        try:
            extracted = FilesToText.file_to_text(file)
            full_request = f"Текст в файле: {extracted}. {user_request}"
        except Exception as e:
            await message.answer("🛠️・Извините, но я не поддерживаю этот формат")
            print(e)
    
    await dialog.add_user_message(full_request)

    content = []
    response_message = await message.answer("Отправка запроса...")

    last_update_time = time.time()
    accumulated_chunks = []
    
    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        async for chunk in ai_client.stream_response(dialog):
            content += chunk[0]
            accumulated_chunks += chunk[0]
            
            current_time = time.time()
            is_final_chunk = chunk[1] is not None and chunk[1]

            if current_time - last_update_time >= 2 or is_final_chunk:
                try:
                    formatted_text = Formattor.format_text("".join(content))[0]
                    await response_message.edit_text(formatted_text, parse_mode="MarkdownV2")
                    accumulated_chunks = []
                    last_update_time = current_time
                except Exception as e:
                    print(f"Update error: {e}")

    final_text_with_files = Formattor.format_text("".join(content))
    
    if not final_text_with_files[0]:
        await response_message.edit_text("👾・Извините, что-то пошло не так! Попробуйте ещё раз")
        dialog.messages.pop()
    else:
        if final_text_with_files[1]:
            if len(final_text_with_files[1]) > 1:
                media_group = MediaGroupBuilder()
                for file in final_text_with_files[1]:
                    document = BufferedInputFile(file[1], filename=file[0])
                    media_group.add(type='document', media=document)
                await message.answer_media_group(media=media_group.build())
            else:
                document = BufferedInputFile(final_text_with_files[1][1], filename=final_text_with_files[1][0])
                await message.answer_document(document)

        
        await dialog.add_assistant_message("".join(content))


@request_router.message()
async def text_request(message: Message, dialog: Dialog, ai_client: DeepSeek, repo: RequestsRepo):
    if len(dialog) > 0 and dialog[-1]['role'] == 'user':
        await message.answer("⏳・Дождитесь ответа на прошлый запрос")
        return

    user_request = message.text
    await dialog.add_user_message(user_request)

    content = []
    response_message = await message.answer("Отправка запроса...")
    
    last_update_time = time.time()
    accumulated_chunks = []
    
    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        async for chunk in ai_client.stream_response(dialog):
            content += chunk[0]
            accumulated_chunks += chunk[0]
            
            current_time = time.time()
            is_final_chunk = chunk[1] is not None and chunk[1]

            if current_time - last_update_time >= 2 or is_final_chunk:
                try:
                    formatted_text = Formattor.format_text("".join(content))[0]
                    await response_message.edit_text(formatted_text, parse_mode="MarkdownV2")
                    accumulated_chunks = []
                    last_update_time = current_time
                except Exception as e:
                    print(f"Update error: {e}")
    
    final_text_with_files = Formattor.format_text("".join(content))

    if not final_text_with_files[0]:
        await response_message.edit_text("👾・Извините, что-то пошло не так! Попробуйте ещё раз")
        dialog.messages.pop()
    else:
        try:
            await response_message.edit_text(final_text_with_files[0], parse_mode="MarkdownV2")
        except Exception as e:
            print(f"Final update error: {e}")
            
        if final_text_with_files[1]:
            if len(final_text_with_files[1]) > 1:
                media_group = MediaGroupBuilder()
                for file in final_text_with_files[1]:
                    document = BufferedInputFile(file[1], filename=file[0])
                    media_group.add(type='document', media=document)
                await message.answer_media_group(media=media_group.build())
            else:
                document = BufferedInputFile(final_text_with_files[1][1], filename=final_text_with_files[1][0])
                await message.answer_document(document)
        
        await dialog.add_assistant_message("".join(content))
