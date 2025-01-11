from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, BotCommand

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.user import get_token


class TokenSet(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | BotCommand,
        data: dict[str, Any]
    ) -> Any:
        get_token_handler = get_flag(data, "token")

        if not get_token_handler:
            return await handler(event, data)

        sessionmaker: async_sessionmaker = data["sessionmaker"]
        redis: Redis = data["redis"]
        user_id = event.from_user.id

        token_in_cache = await redis.hget(user_id, "token")

        if token_in_cache:
            data["user_token"] = token_in_cache
            return await handler(event, data)

        async with sessionmaker() as session:
            async with session.begin():
                token_from_db = await get_token(user_id, session)
                data["user_token"] = token_from_db

                if token_from_db:
                    await redis.hset(user_id, "token", token_from_db)
                return await handler(event, data)
