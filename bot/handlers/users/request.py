import io

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import time

from services.apis.deepseek.dialogs import Dialog
from services.apis.deepseek.deepseek import DeepSeek
from services.apis.deepseek.formatting import Formattor
from services.apis.yandex_api import YandexOCR
from services.database.repo.requests import RequestsRepo
from services.database.models.users import User

from scripts.file_reader import FilesToText

request_router = Router()

active_dialogs = {}

def create_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Остановить"))
    return builder.as_markup(resize_keyboard=True)

async def remove_keyboard(message):
    chat_id = message.chat.id
    if chat_id in active_dialogs:
        old_message = active_dialogs[chat_id]
        await old_message.delete()
        del active_dialogs[chat_id]
        return True
    return False

@request_router.message(Command("reset"))
async def reset_context(message: Message, dialog: Dialog):
    await dialog.clear()
    await message.answer("🗑️・История диалога очищена")


@request_router.message(Command("change"))
async def change_model(message: Message, user: User, repo: RequestsRepo):
    user_model = user.profile.selected_model

    if user_model == 'deepseek-chat':
        await repo.profiles.change_model(user.profile.profile_id, 'deepseek-reasoner')
        await message.answer('👾・Вы сменили модель на DeepSeek-R1 (<b>Глубокие ответы</b>)', parse_mode='HTML')
    else:
        await repo.profiles.change_model(user.profile.profile_id, 'deepseek-chat')
        await message.answer('👾・Вы сменили модель на DeepSeek-V3 (<b>Быстрые ответы</b>)', parse_mode='HTML')


@request_router.message(F.photo)
async def image_request(message: Message, dialog: Dialog, ai_client: DeepSeek, yandex_ocr: YandexOCR, user: User):
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
    base64_image = yandex_ocr.encode_file(image_bytes.getvalue())
    image_text = await yandex_ocr.recognize(base64_image)

    full_request = f"Текст на изображении: {image_text}. {user_request}" if message.caption else f"Текст на изображении: {image_text}."

    if image_text is None:
        await message.answer("👾・Извините, не удалось распознать текст на изображении")
        return

    await dialog.add_user_message(full_request)

    content = ''
    reasoning_content = ''
    active_dialogs[message.chat.id] = await message.answer("⏳・Отправка запроса…", reply_markup=create_keyboard())

    response_message = None

    last_update_time = time.time()

    files = []

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        async for chunk in ai_client.stream_response(dialog, model=user.profile.selected_model):
            if(message.chat.id in active_dialogs):
                await remove_keyboard(message)

            if(response_message is None):
                response_message = await message.answer("⏳・Генерация ответа…")

            if(chunk[1] is not None and chunk[1]):
                reasoning_content += chunk[1]
                if(len(reasoning_content) > 4000):
                    reasoning_content = reasoning_content[:4000] + "…"

            if(chunk[0] is not None and chunk[0]):
                content += chunk[0]

            current_time = time.time()
            is_final_chunk = chunk[2] is not None and chunk[2]

            if current_time - last_update_time >= 2 or is_final_chunk:
                try:
                    if(len(content) > 0):
                        if len(content) > 4005:
                            text = content[:4000] + "…"
                            formatted = Formattor.format_text(text)
                            await response_message.edit_text(formatted[0], parse_mode="MarkdownV2")
                            files = files + formatted[1]
                            content = "…" + content[4000:]
                            formatted_text = Formattor.format_text(content)[0]
                            response_message = await message.answer(formatted_text, parse_mode="MarkdownV2")
                        else:
                            formatted = Formattor.format_text(content)
                            await response_message.edit_text(formatted[0], parse_mode="MarkdownV2")
                    elif reasoning_content is not None and len(reasoning_content) > 0:
                        reasoningData = "```Размышляю...\n" + reasoning_content + "```"
                        await response_message.edit_text(reasoningData, parse_mode="MarkdownV2")  

                    last_update_time = current_time
                except Exception as e:
                    last_update_time = current_time
                    print(f"Update error: {e}", flush=True)

    final_text_with_files = Formattor.format_text(content)

    if not final_text_with_files[0]:
        await response_message.edit_text("👾・Извините, что-то пошло не так! Попробуйте ещё раз")
        dialog.messages.pop()
    else:
        try:
            await response_message.edit_text(final_text_with_files[0], parse_mode="MarkdownV2")
        except Exception as e:
            print(f"Final update error: {e}", flush=True)

        if final_text_with_files[1]:
            media_group = MediaGroupBuilder()
            for file in final_text_with_files[1]:
                document = BufferedInputFile(file[1], filename=file[0])
                media_group.add(type='document', media=document)
            await message.answer_media_group(media=media_group.build())

        await dialog.add_assistant_message("".join(content))


@request_router.message(F.document)
async def document_request(message: Message, dialog: Dialog, ai_client: DeepSeek, yandex_ocr: YandexOCR, user: User):
    if message.media_group_id:
        await message.reply("👾・Отправляйте файлы по одному!")
        return
    if len(dialog) > 0 and dialog[-1]['role'] == 'user':
        await message.answer("⏳・Дождитесь ответа на прошлый запрос")
        return

    user_request = message.caption

    file_id = message.document.file_id
    filename = message.document.file_name
    file_bytes = io.BytesIO()
    
    file_size_mb = message.document.file_size / 1024 / 1024

    response_message = None

    if(file_size_mb > 10):
        full_request = f"Текст в файле: Не удалось прочитать файл, размер файла превышает 10 МБ. {user_request}"
    else:
        active_dialogs[message.chat.id] = await message.answer("⏳・Чтение файла…", reply_markup=create_keyboard())

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

        elif filename.endswith('.pdf'):
            extracted = FilesToText.pdf_to_text(file)
            full_request = f"Текст в файле: {extracted}. {user_request}"

        else:
            try:
                extracted = FilesToText.file_to_text(file)
                full_request = f"Текст в файле: {extracted}. {user_request}"
            except Exception as e:
                await message.answer("🛠️・Извините, но я не поддерживаю этот формат")
                print(e, flush=True)

    await dialog.add_user_message(full_request)

    content = ''
    reasoning_content = ''
    if(active_dialogs[message.chat.id] is not None):
        # edit
        response_message = await message.answer("⏳・Отправка запроса…")
    else:    
        active_dialogs[message.chat.id] = await message.answer("⏳・Отправка запроса…", reply_markup=create_keyboard())

    last_update_time = time.time()

    files = []

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        async for chunk in ai_client.stream_response(dialog, model=user.profile.selected_model):
            if(message.chat.id in active_dialogs):
                await remove_keyboard(message)

            if(response_message is None):
                response_message = await message.answer("⏳・Генерация ответа…")

            if(chunk[1] is not None and chunk[1]):
                reasoning_content += chunk[1]
                if(len(reasoning_content) > 4000):
                    reasoning_content = reasoning_content[:4000] + "…"

            if(chunk[0] is not None and chunk[0]):
                content += chunk[0]

            current_time = time.time()
            is_final_chunk = chunk[2] is not None and chunk[2]

            if current_time - last_update_time >= 2 or is_final_chunk:
                try:
                    if(len(content) > 0):
                        if len(content) > 4005:
                            text = content[:4000] + "…"
                            formatted = Formattor.format_text(text)
                            await response_message.edit_text(formatted[0], parse_mode="MarkdownV2")
                            files = files + formatted[1]
                            content = "…" + content[4000:]
                            formatted_text = Formattor.format_text(content)[0]
                            response_message = await message.answer(formatted_text, parse_mode="MarkdownV2")
                        else:
                            formatted = Formattor.format_text(content)
                            await response_message.edit_text(formatted[0], parse_mode="MarkdownV2")
                    elif reasoning_content is not None and len(reasoning_content) > 0:
                        reasoningData = "```Размышляю...\n" + reasoning_content + "```"
                        await response_message.edit_text(reasoningData, parse_mode="MarkdownV2")  

                    last_update_time = current_time
                except Exception as e:
                    last_update_time = current_time
                    print(f"Update error: {e}", flush=True)

    
    final_text_with_files = Formattor.format_text(content)

    if not final_text_with_files[0]:
        await response_message.edit_text("👾・Извините, что-то пошло не так! Попробуйте ещё раз")
        dialog.messages.pop()
    else:
        try:
            await response_message.edit_text(final_text_with_files[0], parse_mode="MarkdownV2")
        except Exception as e:
            print(f"Final update error: {e}", flush=True)

        if final_text_with_files[1]:
            media_group = MediaGroupBuilder()
            for file in final_text_with_files[1]:
                document = BufferedInputFile(file[1], filename=file[0])
                media_group.add(type='document', media=document)
            await message.answer_media_group(media=media_group.build())

        await dialog.add_assistant_message("".join(content))


@request_router.message()
async def text_request(message: Message, dialog: Dialog, ai_client: DeepSeek, user: User):

    user_request = message.text

    if(user_request == "Остановить"):
        state = await remove_keyboard(message)
        if(state):
            dialog.messages.pop()
            await message.answer("👾・Диалог остановлен", reply_markup=ReplyKeyboardRemove())
        return

    if len(dialog) > 0 and dialog[-1]['role'] == 'user':
        await message.answer("⏳・Дождитесь ответа на прошлый запрос")
        return

    
    
    if(user_request is None or user_request == ""):
        return

    await dialog.add_user_message(user_request)

    

    content = ''
    reasoning_content = ''
    active_dialogs[message.chat.id] = await message.answer("⏳・Отправка запроса…", reply_markup=create_keyboard())

    response_message = None

    last_update_time = time.time()

    files = []

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        async for chunk in ai_client.stream_response(dialog, model=user.profile.selected_model):
            
            if(message.chat.id in active_dialogs):
                await remove_keyboard(message)
            
            if(response_message is None):
                response_message = await message.answer("⏳・Генерация ответа…")

            if(chunk[1] is not None and chunk[1]):
                reasoning_content += chunk[1]
                if(len(reasoning_content) > 4000):
                    reasoning_content = reasoning_content[:4000] + "…"

            if(chunk[0] is not None and chunk[0]):
                content += chunk[0]

            current_time = time.time()
            is_final_chunk = chunk[2] is not None and chunk[2]

            if current_time - last_update_time >= 2 or is_final_chunk:
                try:
                    if(len(content) > 0):
                        if len(content) > 4005:
                            text = content[:4000] + "…"
                            formatted = Formattor.format_text(text)
                            await response_message.edit_text(formatted[0], parse_mode="MarkdownV2")
                            files = files + formatted[1]
                            content = "…" + content[4000:]
                            formatted_text = Formattor.format_text(content)[0]
                            response_message = await message.answer(formatted_text, parse_mode="MarkdownV2")
                        else:
                            formatted = Formattor.format_text(content)
                            await response_message.edit_text(formatted[0], parse_mode="MarkdownV2")
                    elif reasoning_content is not None and len(reasoning_content) > 0:
                        reasoningData = "```Размышляю...\n" + reasoning_content + "```"
                        await response_message.edit_text(reasoningData, parse_mode="MarkdownV2")   

                    last_update_time = current_time
                except Exception as e:
                    last_update_time = current_time
                    print(f"Update error: {e}", flush=True)

    final_text_with_files = Formattor.format_text(content)

    if not final_text_with_files[0]:
        await response_message.edit_text("👾・Извините, что-то пошло не так! Попробуйте ещё раз")
        dialog.messages.pop()
    else:
        try:
            await response_message.edit_text(final_text_with_files[0], parse_mode="MarkdownV2")
        except Exception as e:
            print(f"Final update error: {e}", flush=True)

        if final_text_with_files[1]:
            media_group = MediaGroupBuilder()
            for file in final_text_with_files[1]:
                document = BufferedInputFile(file[1], filename=file[0])
                media_group.add(type='document', media=document)
            await message.answer_media_group(media=media_group.build())

        await dialog.add_assistant_message("".join(content))
