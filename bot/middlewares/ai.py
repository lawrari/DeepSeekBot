from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.apis.deepseek.dialogs import Dialogs
from services.apis.deepseek.deepseek import DeepSeek
from services.apis.yandex_api import YandexOCR


class AiMiddleware(BaseMiddleware):
    def __init__(self, dialogs: Dialogs, deepseek_client: DeepSeek, yandex_client: YandexOCR) -> None:
        self.dialogs = dialogs
        self.deepseek_client = deepseek_client
        self.yandex_client = yandex_client

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.text or event.photo or event.document:
            if event.from_user.id not in self.dialogs:
                await self.dialogs.create_dialog(event.from_user.id)
                await self.dialogs.remove_old_dialogs()

        data['dialogs'] = self.dialogs
        data['dialog'] = self.dialogs.dialogs.get(event.from_user.id)
        data['ai_client'] = self.deepseek_client
        data['yandex_ocr'] = self.yandex_client
        result = await handler(event, data)
        return result
