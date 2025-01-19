from typing import Any

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware, get_i18n

from aiogram_dialog import Data, DialogManager
from aiogram_dialog.widgets.kbd import Button

from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from .states import ProjectSG
from .utils import get_token, get_headers, get_lang_and_tz
from db.user import User, get_user
from handlers.bugtracker_api import Project, get_token as get_token_api


async def start_texts_getter(**kwargs):
    text = _(
        """\
            Hello!
            \nA quick guide to working with me:
            \n1) Login: first step is log in via /login command. Without it, I won't work!
            \n2) A real starting menu accessed via /projects command.
            \n3) From there, you can view all your projects and create new ones.
            \n4) Next, you can view the issues related to this project, edit the project, or delete it altogether.
            \n5) Everything listed in the 3-4) is also relevant for issues.
            \n6) You can also change my settings: language and time zone via /settings command.
            \n<b>Please note that you must already be registered through the website or API. If you don't have an account yet, then you need to create one and only then use me. </b>
        """  # noqa: E501
    )
    login_btn = _("Login")
    projects_btn = _("Projects")
    settings_btn = _("Settings")

    return {
        "start_text": text,
        "login_btn": login_btn,
        "projects_btn": projects_btn,
        "settings_btn": settings_btn
    }


async def login_email_getter(
    dialog_manager: DialogManager,
    redis: Redis,
    sessionmaker: async_sessionmaker,
    **kwargs
):
    user_id = dialog_manager.event.from_user.id

    if await get_token(sessionmaker, redis, user_id):
        await dialog_manager.done(_("You're already logged in."))
    return {"email_text": _("Enter email:")}


async def login_password_getter(**kwargs):
    return {"password_text": _("Enter password:")}


async def login_results_getter(
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
            "results": token["error"],
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

    await dialog_manager.done(_("Successful login!"))


async def settings_texts_getter(**kwargs):
    return {
        "settings_text": _("Choose what you want to change:"),
        "language_btn": _("Language"),
        "timezone_btn": _("Timezone"),
        "language_text": _("Select a language:"),
        "en_btn": "English 🇺🇸",
        "ru_btn": "Русский 🇷🇺",
        "timezone_text": _("Select the time zone:"),
        "UTC": "UTC",
        "Moscow": _("Moscow"),
        "Vladivostok": _("Vladivostok")
    }


async def language_setter(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    i18n_middleware: FSMI18nMiddleware = manager.middleware_data["i18n_middleware"]  # noqa: E501
    state: FSMContext = manager.middleware_data["state"]
    redis: Redis = manager.middleware_data["redis"]

    current_language = get_i18n().current_locale
    language = button.widget_id

    if current_language == language:
        return await manager.done(_("This language is already set."))
    else:
        await i18n_middleware.set_locale(state, language)
        await redis.hset(callback.from_user.id, "language", language)

        async with sessionmaker.begin() as session:
            user = User(user_id=callback.from_user.id, language=language)
            await session.merge(user)

        await manager.done(_("You have changed the language!"))


async def timezone_setter(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    state: FSMContext = manager.middleware_data["state"]
    redis: Redis = manager.middleware_data["redis"]

    tz = button.widget_id
    cur_tz = await redis.hget(callback.from_user.id, "timezone")

    if cur_tz == "Europe/Moscow" or cur_tz == "Asia/Vladivostok":
        cur_tz = cur_tz.split("/")[1]

    if cur_tz == tz:
        return await manager.done(_("This time zone is already set."))

    if tz == "Moscow":
        tz = "Europe/Moscow"
    elif tz == "Vladivostok":
        tz = "Asia/Vladivostok"

    await redis.hset(callback.from_user.id, "timezone", tz)
    async with sessionmaker.begin() as session:
        user = await get_user(callback.from_user.id, session)
        user = User(user_id=callback.from_user.id, timezone=tz)
        await session.merge(user)

    await state.update_data(timezone=tz)
    await manager.done(_("You have changed the time zone!"))


async def process_result(
    start_data: Data,
    result: Any,
    dialog_manager: DialogManager
):
    if result:
        dialog_manager.dialog_data["result"] = result


async def projects_texts_getter(*args, **kwargs):
    return {
        "projects_text": _("Your projects:"),
        "zero_projects": _("You don't have projects yet."),
        "back": _("Back"),
        "cancel": _("Cancel"),
        "create": _("Create new"),
        "name_text": _("Enter project name:"),
        "key_text": _("Enter key of the project:"),
        "starred_text": _("Is this project will be a favorite:"),
        "true": _("True"),
        "false": _("False"),
    }


async def projects_getter(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    user_headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    if user_headers is not None:
        # Limit in 9999 projects (default is 10)
        # is necessary to get pagination working.
        projects = await Project.get_items(session, user_headers, {"limit": 9999})

        if "count" in projects:
            return {"projects": projects["results"]}
        return {"no_projects": projects["detail"]}
    else:
        return {"need_log_in": _("You aren't logged in, use /login command.")}


async def clicked_starred(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    dialog_manager.dialog_data["starred"] = callback.data


async def clicked_project(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(ProjectSG.details, dialog_manager.item_id)


async def create_project(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    user_headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis,
    )
    data = {
        "name": dialog_manager.find("name").get_value(),
        "key": dialog_manager.find("key").get_value().upper(),
        "starred": dialog_manager.dialog_data["starred"],
    }
    results = await Project().create_item(session, user_headers, data)

    if "error" in results:
        return {
            "results": results["error"],
            "try_again": _("Try again")
        }

    await dialog_manager.done(results["success"])


async def project_texts_getter(*args, **kwargs):
    return {
        "issues": _("Issues"),
        "edit": _("Edit"),
        "delete": _("Delete"),
        "back": _("Back")
    }


async def project_getter(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    project_id = dialog_manager.start_data
    user_headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    lang, tz = await get_lang_and_tz(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    project = await Project.get_item(session, project_id, user_headers, lang, tz)

    formatted_project = _(
        """
            <b>Name</b>: {name}\
            \n<b>Key</b>: {key}\
            \n<b>Favorite</b>: {starred}\
            \n<b>Created</b>: {created}\
            \n<b>Updated</b>: {updated}
        """
    ).format(
        name=project['name'],
        key=project['key'],
        starred=Project.get_translated_starred(project["starred"]),
        created=project['created'],
        updated=project['updated']
    )

    return {"project": formatted_project}


async def delete_project(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    redis: Redis = manager.middleware_data["redis"]
    session: ClientSession = manager.middleware_data["session"]

    project_id = manager.start_data
    user_headers = await get_headers(
        user_id=manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    result = await Project.delete_item(session, project_id, user_headers)

    if "success" in result:
        return await manager.done(result["success"])
    manager.dialog_data["error"] = result["error"]
    return
