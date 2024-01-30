from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, BotCommand

from db.user import get_headers, get_user_language, get_user_timezone


class Headers(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | BotCommand,
        data: Dict[str, Any]
    ) -> Any:
        set_headers = get_flag(data, "set_headers")
        lang_tz = get_flag(data, "lang_tz")

        if not set_headers and not lang_tz:
            return await handler(event, data)
        
        sessionmaker = data["sessionmaker"]
        
        if set_headers and lang_tz:
            async with sessionmaker() as session:
                async with session.begin():

                    timezones = {
                        "UTC": "UTC",
                        "Moscow": "Europe/Moscow",
                        "Vladivostok": "Asia/Vladivostok"
                    }

                    results_headers = await get_headers(event.from_user.id, session)
                    results_language = await get_user_language(user_id = event.from_user.id, session=session)
                    results_timezone = await get_user_timezone(user_id = event.from_user.id, session=session)

                    headers = results_headers.fetchone()[0]
                    lang = results_language.fetchone()[0]
                    tz = results_timezone.fetchone()[0]

                    data["user_headers"] = headers
                    data["language"] = lang
                    data["timezone"] = timezones[tz]

        else:
            async with sessionmaker() as session:
                async with session.begin():
                    results = await get_headers(event.from_user.id, session)
                    headers = results.fetchone()[0]

                    data["user_headers"] = headers

        return await handler(event, data)
