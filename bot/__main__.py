import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from config.config import load_config, Config
from services.database.setup import create_engine, create_session_pool
from bot.handlers import routers_list
from bot.middlewares.config import ConfigMiddleware
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.referral import ReferralMiddleware
from bot.middlewares.ai import AiMiddleware
from bot.middlewares.yookassa import YookassaMiddleware
from bot.utils import broadcaster
from services.apis.deepseek.dialogs import Dialogs
from services.apis.deepseek.deepseek import DeepSeek
from services.apis.yandex_api import YandexOCR
from services.apis.payments.yookassa_helper import YooKassaHelper


from bot.handlers import (referral_start_router,
                          admin_start_router,
                          maintenance_router,
                          payments_router,
                          request_router,
                          user_start_router)

from services.database.models import Base


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Bot started!")

    await bot.set_my_commands(commands=[BotCommand(command='start', description='Меню')])


def register_global_middlewares(dp: Dispatcher, config: Config, dialogs: Dialogs, deepseek_client: DeepSeek, yandex_client: YandexOCR):
    middleware_types = [
        ConfigMiddleware(config),
        AiMiddleware(dialogs, deepseek_client, yandex_client)
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)
    

def register_database_middleware(session_pool=None):
    user_start_router.message.outer_middleware(DatabaseMiddleware(session_pool))
    user_start_router.callback_query.outer_middleware(DatabaseMiddleware(session_pool))
    request_router.message.outer_middleware(DatabaseMiddleware(session_pool))
    referral_start_router.message.outer_middleware(ReferralMiddleware(session_pool))
    payments_router.message.outer_middleware(DatabaseMiddleware(session_pool))



def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """

    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot...")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """

    if config.telegram_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)

    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    
    properties = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=config.telegram_bot.token, properties=properties)
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    dialogs = Dialogs()
    deepseek_client = DeepSeek(config.misc.deepseek_api_key)
    yandex_client = YandexOCR(config.misc.yandex_api_key)
    yookassa_client = YooKassaHelper(config.misc.yookassa_shop_id, config.misc.yookassa_secret_key)

    register_global_middlewares(dp, config, dialogs, deepseek_client, yandex_client)
    register_database_middleware(session_pool)
    payments_router.message.outer_middleware(YookassaMiddleware(yookassa_client))

    await on_startup(bot, config.telegram_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
