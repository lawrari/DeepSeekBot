from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.apis.DeepSeek.dialogs import Dialogs
from services.apis.DeepSeek.deepseek import DeepSeek


class AiMiddleware(BaseMiddleware):
    def __init__(self, dialogs: Dialogs, client: DeepSeek) -> None:
        self.dialogs = dialogs
        self.client = client

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.text or event.photo:
            if event.from_user.id not in self.dialogs:
                await self.dialogs.create_dialog(event.from_user.id)
                await self.dialogs.remove_old_dialogs()

        data['dialogs'] = self.dialogs
        data['dialog'] = self.dialogs.dialogs.get(event.from_user.id)
        data['ai_client'] = self.client
        result = await handler(event, data)
        return result
