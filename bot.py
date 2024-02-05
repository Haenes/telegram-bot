import os
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from sqlalchemy.engine import URL

from redis.asyncio import Redis

from db.base import BaseModel
from db.engine import make_async_engine, get_sessionmaker, proceed_schemas

from middlewares.user_token import TokenSet
from middlewares.user_headers import Headers

from handlers import start, common
from handlers.project import projects, pagination_projects,  create_project, update_project
from handlers.issue import issues, pagination_issues, create_issue, update_issue


async def main():
    load_dotenv()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    logging.basicConfig(level=logging.INFO)

    i18n = I18n(path="locale", default_locale="en", domain="bot")
    i18n_middleware = FSMI18nMiddleware(i18n, "lang")

    # Redis setup
    redis = Redis(decode_responses=True)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=RedisStorage(redis))

    # register all midllewares
    dp.update.middleware.register(i18n_middleware)
    dp.message.middleware.register(TokenSet())
    dp.message.middleware.register(Headers())
    dp.callback_query.middleware.register(Headers())
    

    dp.include_routers(start.router, projects.router, pagination_projects.router, issues.router, pagination_issues.router)
    dp.include_routers(common.router, create_project.router, update_project.router, create_issue.router, update_issue.router)


    # SQLAlchemy setup
    psql_url = URL.create(
        "postgresql+asyncpg",
        os.environ.get("PSQL_USERNAME"),
        os.environ.get("PSQL_PASSWORD"),
        os.environ.get("PSQL_HOST"),
        os.environ.get("PSQL_PORT"),
        os.environ.get("PSQL_DATABASE"))

    async_engine = make_async_engine(psql_url)
    sessionmaker = get_sessionmaker(async_engine)
    await proceed_schemas(async_engine, BaseModel.metadata)


    # Launch the bot and skip all the accumulated updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, sessionmaker=sessionmaker, redis=redis)


if __name__ == "__main__":
    asyncio.run(main())
