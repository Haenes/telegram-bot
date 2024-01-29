from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, BotCommand

from db.user import get_token


class TokenSet(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | BotCommand,
        data: Dict[str, Any]
    ) -> Any:
        token = get_flag(data, "token")
        if not token:
            return await handler(event, data)
        
        sessionmaker = data["sessionmaker"]
        
        async with sessionmaker() as session:
            async with session.begin():
                results = await get_token(event.from_user.id, session)
                token = results.fetchone()[0]

                if token:
                     data["user_token"] = token
                else:
                    data["user_token"] = None
                    return await handler(event, data)

        return await handler(event, data)
