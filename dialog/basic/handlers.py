from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware, get_i18n

from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.input import ManagedTextInput

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.user import User, get_user


async def handle_login_input(
    message: Message,
    text: ManagedTextInput,
    manager: DialogManager,
    input: str
):
    manager.show_mode = ShowMode.EDIT
    await message.delete()
    await manager.next()


async def set_language(
    callback: CallbackQuery,
    select: Select,
    manager: DialogManager,
    language: str
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    i18n_middleware: FSMI18nMiddleware = manager.middleware_data["i18n_middleware"]  # noqa: E501
    state: FSMContext = manager.middleware_data["state"]
    redis: Redis = manager.middleware_data["redis"]
    current_language = get_i18n().current_locale

    if current_language == language:
        return await manager.done(_("This language is already set."))
    else:
        await i18n_middleware.set_locale(state, language)
        await redis.hset(callback.from_user.id, "language", language)

        async with sessionmaker.begin() as session:
            user = User(user_id=callback.from_user.id, language=language)
            await session.merge(user)

        await manager.done(_("You have changed the language!"))


async def set_timezone(
    callback: CallbackQuery,
    select: Select,
    manager: DialogManager,
    timezone: str
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    state: FSMContext = manager.middleware_data["state"]
    redis: Redis = manager.middleware_data["redis"]

    current_timezone = await redis.hget(callback.from_user.id, "timezone")

    if current_timezone == timezone:
        return await manager.done(_("This time zone is already set."))

    async with sessionmaker.begin() as session:
        user = await get_user(callback.from_user.id, session)
        user = User(user_id=callback.from_user.id, timezone=timezone)
        await session.merge(user)

    await redis.hset(callback.from_user.id, "timezone", timezone)
    await state.update_data(timezone=timezone)
    await manager.done(_("You have changed the time zone!"))
