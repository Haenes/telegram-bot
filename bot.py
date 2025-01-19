import os
import asyncio
import logging
from dotenv import load_dotenv

from aiohttp import ClientSession

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from aiogram_dialog import setup_dialogs

from redis.asyncio import Redis
from db.engine import async_session_maker

from dialog.dialogs import (
    start as start_dialog,
    login,
    settings,
    projects as projects_dialog,
    create_project,
    project
)

from handlers import start, common
from handlers.project import projects, update_project
from handlers.issue import (
    issues,
    pagination_issues,
    create_issue,
    update_issue
)


async def main():
    load_dotenv()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    logging.basicConfig(level=logging.INFO)

    i18n = I18n(path="locale", default_locale="en", domain="bot")
    i18n_middleware = FSMI18nMiddleware(i18n)

    # Redis setup
    redis = Redis(
        host=os.environ.get("REDIS_HOST"),
        password=os.environ.get("REDIS_PASSWORD"),
        username=os.environ.get("REDIS_USER"),
        decode_responses=True
    )

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=RedisStorage(redis, DefaultKeyBuilder(with_destiny=True)))

    # register all midllewares
    dp.update.middleware.register(i18n_middleware)

    dp.include_routers(
        start.router,
        common.router,
        pagination_issues.router
    )
    dp.include_routers(
        projects.router,
        update_project.router,
        issues.router,
        create_issue.router,
        update_issue.router
    )
    dp.include_routers(
        start_dialog,
        login,
        settings,
        projects_dialog,
        create_project,
        project
    )

    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        sessionmaker=async_session_maker,
        redis=redis,
        session=ClientSession(trust_env=True)
    )


if __name__ == "__main__":
    asyncio.run(main())
