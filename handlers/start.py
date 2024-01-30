from aiogram import Router, types, F
from aiogram.filters import CommandObject
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.i18n import gettext as _

from db.user import User, get_user
from handlers.bugtracker_api import get_token
from keyboards.for_menu import menu_kb
from keyboards.for_settings import settings_kb, language_kb, timezone_kb


router = Router()


class UserSettings(StatesGroup):
    lang = State()


@router.message(Command("start"), flags={"action":"get_user"})
async def cmd_start(message: types.Message, state: FSMContext, language, i18n_middleware):
    user = message.from_user.first_name

    if language:
        await state.update_data(lang = language)
        await i18n_middleware.set_locale(state, language)

    if language:
        await state.update_data(lang = language)
        await i18n_middleware.set_locale(state, language)

    text = _("""
\nA quick guide to working with me: 
\n1) Login: first step is log in via /login command. Without it, I won't work!
\n2) Main menu accessed via /menu command. Here you can choose what to work with: projects or issues.
\n3) Then you can create a new item (project or issue), view information about it or other items.
\n4) After that, you can change the data of the selected item or delete it altogether!
\n5) You can also change my settings: language and time zone via /settings command.
\n<b>Please note that you must already be registered through the website. If you don't have an account yet, then you need to create one and only then use me. </b>
           """)

    await message.answer(_("Hello, {user}! {text}").format(user=user, text=text), parse_mode="HTML")


@router.message(Command("login"), flags={"token":"get_token"})
async def cmd_login(message: types.Message, command:CommandObject, sessionmaker, user_token):
    if command.args:
        data = command.args.split(" ")
        username, password = data[0], data[1]
    else:
        if user_token and user_token != None:
            await message.reply(_("You're already logged in, use the /menu command."))
            await message.delete()
        else:
            await message.answer(_("Please, enter your <u>username and password</u> after /login command! \nExample: /login USERNAME PASSWORD"), parse_mode="HTML")

    if user_token == None:
        try:
            token = get_token(username, password)
            headers = {"Authorization": f"Token {token}"}

            async with sessionmaker() as session:
                async with session.begin():
                    user = User(user_id = message.from_user.id, user_token = token, user_headers = headers)
                    await session.merge(user)

            await message.reply(_("Successful login! \nTo continue, enter /menu command."))
            await message.delete()
        except KeyError:
            await message.reply(_("Invalid username/password!"))


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer(_("From here, u can see all of yours <b>Projects</b> and <b>Issues</b>."), parse_mode="HTML", reply_markup=menu_kb())


@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    await message.answer(_("Choose what you want to change:"), parse_mode="HTML", reply_markup=settings_kb())


@router.callback_query(F.data == "language")
async def language(callback: types.CallbackQuery):
    await callback.message.answer(_("Select a language:"), parse_mode="HTML", reply_markup=language_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"), F.data.as_("language"))
async def set_language(callback: types.CallbackQuery, state: FSMContext, language: types.CallbackQuery, i18n_middleware, sessionmaker):
    lang = language.removeprefix("lang_")

    await i18n_middleware.set_locale(state, lang)

    async with sessionmaker() as session:
        async with session.begin():
            user = User(user_id = callback.from_user.id, language = lang)
            await session.merge(user)

    await state.update_data(lang=lang)
    await callback.message.answer(text=_("You have changed the language!"))
    await callback.answer()


@router.callback_query(F.data == "timezone")
async def timezone(callback: types.CallbackQuery):
    await callback.message.answer(_("Select the time zone:"), parse_mode="HTML", reply_markup=timezone_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("time_"), F.data.as_("timezone"))
async def set_timezone(callback: types.CallbackQuery, timezone: types.CallbackQuery, sessionmaker):
    tz = timezone.removeprefix("time_")

    async with sessionmaker() as session:
        async with session.begin():
            user = await get_user(callback.from_user.id, session)
            user = User(user_id = callback.from_user.id, timezone = tz)
            await session.merge(user)

    await callback.message.answer(text=_("You have changed the timezone!"))
    await callback.answer()
