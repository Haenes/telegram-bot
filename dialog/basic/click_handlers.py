from aiogram.utils.i18n import gettext as _, get_i18n

from aiogram_dialog import DialogManager

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.user import User
from dialog.bugtracker_api import get_token as get_token_api


async def login_user(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    session: ClientSession,
    **kwargs
):
    email = dialog_manager.find("email").get_value()
    password = dialog_manager.find("password").get_value()

    token = await get_token_api(session, email, password)

    if isinstance(token, dict):
        return {
            "error": token["error"],
            "try_again": _("Try again")
        }

    language = get_i18n().current_locale

    async with sessionmaker.begin() as session:
        user = User(
            user_id=dialog_manager.event.from_user.id,
            user_token=token,
            language=language
        )
        await session.merge(user)

    return {"success": _("Successful login!")}
