from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.database.repo.requests import RequestsRepo


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            repo = RequestsRepo(session)

            user = await repo.users.get_or_create_user_and_profile(
                telegram_id=event.from_user.id,
                username=event.from_user.username,
                full_name=event.from_user.full_name,
                language=event.from_user.language_code,
            )

            data['user'] = user
            data['repo'] = repo
            data['session'] = session

            result = await handler(event, data)
        return result
