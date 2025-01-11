from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandObject
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware, get_i18n

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.user import User, get_user
from handlers.bugtracker_api import get_token
from keyboards.for_settings import settings_kb, language_kb, timezone_kb


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user.first_name
    text = _(
        """
            \nA quick guide to working with me:
            \n1) Login: first step is log in via /login command. Without it, I won't work!
            \n2) A real starting menu accessed via /projects command.
            \n3) From there, you can view all your projects and create new ones.
            \n4) Next, you can view the issues related to this project, edit the project, or delete it altogether.
            \n5) Everything listed in the 3-4) is also relevant for issues.
            \n6) You can also change my settings: language and time zone via /settings command.
            \n<b>Please note that you must already be registered through the website or API. If you don't have an account yet, then you need to create one and only then use me. </b>
        """
    )
    await message.answer(_("Hello, {user}!{text}").format(user=user, text=text))


@router.message(Command("login"), flags={"token": "get_token"})
async def cmd_login(
    message: Message,
    command: CommandObject,
    sessionmaker: async_sessionmaker,
    user_token: str | None
):
    if command.args and user_token is None:
        data = command.args.split(" ")
        email, password = data[0], data[1]
        token = await get_token(email, password)

        if isinstance(token, dict):
            return await message.reply(token["error"])

        language = get_i18n().current_locale

        async with sessionmaker() as session:
            async with session.begin():
                user = User(
                    user_id=message.from_user.id,
                    user_token=token,
                    language=language
                )
                await session.merge(user)

        await message.reply(
            _("Successful login! \nTo continue, enter /projects command.")
        )
        await message.delete()

    elif user_token is not None:
        await message.reply(
            _("You're already logged in, use the /projects command.")
        )
        await message.delete()
    else:
        await message.answer(
            _(
                "Please, enter your <u>email and password</u>"
                " after /login command! \nExample: /login EMAIL PASSWORD"
            ),
        )


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    await message.answer(
        _("Choose what you want to change:"),
        reply_markup=settings_kb()
    )


@router.callback_query(F.data == "language")
async def language(callback: CallbackQuery):
    await callback.message.answer(
        _("Select a language:"),
        reply_markup=language_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"), F.data.as_("language"))
async def set_language(
    callback: CallbackQuery,
    language: str,
    state: FSMContext,
    i18n_middleware: FSMI18nMiddleware,
    sessionmaker: async_sessionmaker,
    redis: Redis
):
    language = language.removeprefix("lang_")
    current_language = get_i18n().current_locale

    if current_language == language:
        await callback.message.answer(_("This language is already set."))
        await callback.answer()
    else:
        await i18n_middleware.set_locale(state, language)
        await redis.hset(callback.from_user.id, "language", language)

        async with sessionmaker() as session:
            async with session.begin():
                user = User(user_id=callback.from_user.id, language=language)
                await session.merge(user)

        await callback.message.answer(_("You have changed the language!"))
        await callback.answer()


@router.callback_query(F.data == "timezone")
async def timezone(callback: CallbackQuery):
    await callback.message.answer(
        _("Select the time zone:"),
        reply_markup=timezone_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("time_"), F.data.as_("timezone"))
async def set_timezone(
    callback: CallbackQuery,
    timezone: str,
    state: FSMContext,
    sessionmaker: async_sessionmaker,
    redis: Redis
):
    tz = timezone.removeprefix("time_")
    cur_tz = await redis.hget(callback.from_user.id, "timezone")

    if cur_tz == "Europe/Moscow" or cur_tz == "Asia/Vladivostok":
        cur_tz = cur_tz.split("/")[1]

    if cur_tz == tz:
        await callback.message.answer(_("This time zone is already set."))
        return await callback.answer()

    if tz == "Moscow":
        tz = "Europe/Moscow"
    elif tz == "Vladivostok":
        tz = "Asia/Vladivostok"

    await redis.hset(callback.from_user.id, "timezone", tz)
    async with sessionmaker() as session:
        async with session.begin():
            user = await get_user(callback.from_user.id, session)
            user = User(user_id=callback.from_user.id, timezone=tz)
            await session.merge(user)

    await state.update_data(timezone=tz)
    await callback.message.answer(_("You have changed the time zone!"))
    await callback.answer()
