from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery

from db.user import get_user_language, get_user_timezone


class SetLangAndTz(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        lang_tz = get_flag(data, "lang_tz")
        if not lang_tz:
            return await handler(event, data)

        sessionmaker = data["sessionmaker"]

        async with sessionmaker() as session:
            async with session.begin():
                timezones = {
                    "UTC": "UTC",
                    "Moscow": "Europe/Moscow",
                    "Vladivostok": "Asia/Vladivostok"
                }

                res1 = await get_user_language(user_id = event.from_user.id, session=session)
                res2 = await get_user_timezone(user_id = event.from_user.id, session=session)
                lang = res1.fetchone()[0]
                tz = res2.fetchone()[0]
                data["language"] = lang
                data["timezone"] = timezones[tz]

        return await handler(event, data)