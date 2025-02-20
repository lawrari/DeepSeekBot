from aiogram.filters import BaseFilter
from aiogram.types import Message

from config.config import Config


class MaintenanceFilter(BaseFilter):
    maintenance: bool = True

    async def __call__(self, obj: Message, config: Config) -> bool:
        return config.misc.bot_maintenance == self.maintenance
