from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, BotCommand

from db.user import get_headers


class Headers(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | BotCommand,
        data: Dict[str, Any]
    ) -> Any:
        set_headers = get_flag(data, "set_headers")
        if not set_headers:
            return await handler(event, data)

        sessionmaker = data["sessionmaker"]

        async with sessionmaker() as session:
            async with session.begin():
                results = await get_headers(event.from_user.id, session)
                headers = results.fetchone()[0]

                data["user_headers"] = headers

        return await handler(event, data)
