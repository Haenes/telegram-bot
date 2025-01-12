import ast
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, BotCommand

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.user import get_headers, get_user_language, get_user_timezone


class Headers(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | BotCommand,
        data: dict[str, Any]
    ) -> Any:
        set_headers_flag = get_flag(data, "set_headers")
        lang_tz_flag = get_flag(data, "lang_tz")
        user_id = event.from_user.id

        if not set_headers_flag and not lang_tz_flag:
            return await handler(event, data)

        sessionmaker: async_sessionmaker = data["sessionmaker"]
        redis: Redis = data["redis"]

        if set_headers_flag and lang_tz_flag:
            data_from_cache = await redis.hmget(
                name=event.from_user.id,
                keys=["headers", "language", "timezone"]
            )

            if data_from_cache and data_from_cache.count(None) == 0:
                data["user_headers"], data["language"], data["timezone"] = (
                    ast.literal_eval(data_from_cache[0]),
                    data_from_cache[1],
                    data_from_cache[2]
                )
                return await handler(event, data)

            await set_headers_lang_tz_from_db(sessionmaker, redis, user_id, data)
            return await handler(event, data)

        headers_in_cache = await redis.hget(user_id, "headers")

        if headers_in_cache:
            data["user_headers"] = ast.literal_eval(headers_in_cache)
            return await handler(event, data)

        await set_headers_from_db(sessionmaker, redis, user_id, data)
        return await handler(event, data)


async def set_headers_from_db(
    sessionmaker: async_sessionmaker,
    redis: Redis,
    user_id: int,
    data: dict[str, Any]
):
    async with sessionmaker.begin() as session:
        headers_from_db = await get_headers(user_id, session)
        data["user_headers"] = headers_from_db

    await redis.hset(user_id, "headers", str(headers_from_db))


async def set_headers_lang_tz_from_db(
    sessionmaker: async_sessionmaker,
    redis: Redis,
    user_id: int,
    data: dict[str, Any]
):
    timezones = {
        "UTC": "UTC",
        "Europe/Moscow": "Europe/Moscow",
        "Asia/Vladivostok": "Asia/Vladivostok"
    }

    async with sessionmaker.begin() as session:

        headers_from_db = await get_headers(user_id, session)
        language_from_db = await get_user_language(user_id, session)
        timezone_from_db = await get_user_timezone(user_id, session)

        data["user_headers"] = headers_from_db
        data["language"] = language_from_db
        data["timezone"] = timezones[timezone_from_db]

    await redis.hset(
        name=user_id,
        mapping={
            "headers": str(headers_from_db),
            "language": language_from_db,
            "timezone": timezones[timezone_from_db]
        }
    )
