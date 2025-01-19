from ast import literal_eval

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.user import (
    get_token as get_token_db,
    get_headers as get_headers_db,
    get_user_language,
    get_user_timezone
)


async def get_token(
    sessionmaker: async_sessionmaker,
    redis: Redis,
    user_id: int
):
    token_in_cache = await redis.hget(user_id, "token")

    if token_in_cache:
        return token_in_cache

    async with sessionmaker.begin() as session:
        token_from_db = await get_token_db(user_id, session)

    if token_from_db:
        await redis.hset(user_id, "token", token_from_db)
        return token_from_db


async def get_headers(
    user_id: int,
    sessionmaker: async_sessionmaker,
    redis: Redis,
):
    headers_in_cache = await redis.hget(user_id, "headers")

    if headers_in_cache:
        return literal_eval(headers_in_cache)

    headers_from_db = await set_headers_from_db(sessionmaker, redis, user_id)
    return headers_from_db


async def get_lang_and_tz(
    user_id: int,
    sessionmaker: async_sessionmaker,
    redis: Redis,
):
    lang_tz_from_cache = await redis.hmget(
        name=user_id,
        keys=["language", "timezone"]
    )

    if lang_tz_from_cache and lang_tz_from_cache.count(None) == 0:
        return lang_tz_from_cache[0], lang_tz_from_cache[1]

    lang, tz = await set_lang_and_tz_from_db(sessionmaker, redis, user_id)
    return lang, tz


async def set_headers_from_db(
    sessionmaker: async_sessionmaker,
    redis: Redis,
    user_id: int,
):
    async with sessionmaker.begin() as session:
        headers_from_db = await get_headers_db(user_id, session)

    await redis.hset(user_id, "headers", str(headers_from_db))
    return headers_from_db


async def set_lang_and_tz_from_db(
    sessionmaker: async_sessionmaker,
    redis: Redis,
    user_id: int,
):
    timezones = {
        "UTC": "UTC",
        "Europe/Moscow": "Europe/Moscow",
        "Asia/Vladivostok": "Asia/Vladivostok"
    }

    async with sessionmaker.begin() as session:
        language_from_db = await get_user_language(user_id, session)
        timezone_from_db = await get_user_timezone(user_id, session)

    await redis.hset(
        name=user_id,
        mapping={
            "language": language_from_db,
            "timezone": timezones[timezone_from_db]
        }
    )
    return language_from_db, timezones[timezone_from_db]
