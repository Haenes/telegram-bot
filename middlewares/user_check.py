from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message

from db.user import User, get_user, get_user_language


class UserCheck(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        start = get_flag(data, "action")
        if not start:
            return await handler(event, data)

        sessionmaker = data["sessionmaker"]

        async with sessionmaker() as session:
            async with session.begin():
                user = await get_user(event.from_user.id, session)

                if user is not None:
                    res = await get_user_language(user_id = event.from_user.id, session=session)
                    data["language"] = res.fetchone()[0]
                else:
                    user = User(user_id = event.from_user.id)
                    await session.merge(user)

        return await handler(event, data)
