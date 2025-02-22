from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.apis.payments.yookassa_helper import YooKassaHelper


class YookassaMiddleware(BaseMiddleware):
    def __init__(self, yookassa_helper: YooKassaHelper) -> None:
        self.helper = yookassa_helper

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data['yookassa_helper'] = self.helper    

        result = await handler(event, data)
        return result
