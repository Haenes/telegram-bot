from typing import Any

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware, get_i18n

from aiogram_dialog import Data, DialogManager
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Button

from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from .states import (
    ProjectSG,
    EditProjectSG,
    IssuesSG,
    IssueSG,
    CreateIssueSG,
    EditIssueSG
)
from .utils import get_token, get_headers, get_lang_and_tz
from db.user import User, get_user
from handlers.bugtracker_api import Project, Issue, get_token as get_token_api


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


async def projects_texts(*args, **kwargs):
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


async def create_project_texts(*args, **kwargs):
    return {
        "cancel": _("Cancel"),
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
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    if headers is not None:
        # Limit in 9999 projects (default is 10)
        # is necessary to get pagination working.
        projects = await Project.get_items(session, headers, {"limit": 9999})

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


async def clicked_issues(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(IssuesSG.main, dialog_manager.start_data)


async def clicked_issue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    # Pass project_id and issue_id.
    start_data = dialog_manager.start_data, dialog_manager.item_id
    await dialog_manager.start(IssueSG.details, start_data)


async def clicked_create_new_issue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(CreateIssueSG.title, dialog_manager.start_data)


async def handle_issue_title(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    data: str = None,
):
    manager.dialog_data["title"] = data

    # If all issue data is already set except title (because of the error)
    # don't receive the remaining data again and create the issue immediately.
    if "error_title" in manager.dialog_data:
        del manager.dialog_data["error_title"]
        return await create_issue(callback, button, manager)
    await manager.next()


async def clicked_issue_type(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["type"] = data
    await dialog_manager.next()


async def clicked_issue_priority(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["priority"] = data
    await dialog_manager.next()


async def clicked_issue_status(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["status"] = data
    await create_issue(callback, button, dialog_manager)


async def create_project(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis,
    )
    data = {
        "name": dialog_manager.find("name").get_value(),
        "key": dialog_manager.find("key").get_value().upper(),
        "starred": dialog_manager.dialog_data["starred"],
    }
    results = await Project().create_item(session, headers, data)

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
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    lang, tz = await get_lang_and_tz(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    project = await Project.get_item(session, project_id, headers, lang, tz)

    formatted_project = _(
        """\
            \n<b>Name</b>: {name}\
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


async def clicked_edit_project(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(EditProjectSG.select, dialog_manager.start_data)


async def project_edit_texts_getter(*args, **kwargs):
    return {
        "instructions": _("Select what you want to change:"),
        "fields": [
            (_("Name"), 1),
            (_("Key"), 2),
            (_("Favorite"), 3)
        ],
        "name_text": _("Enter new name:"),
        "key_text": _("Enter new key:"),
        "starred_text": _("Is this project will be a favorite:"),
        "true": _("True"),
        "false": _("False"),
        "continue": _("Continue"),
        "cancel": _("Cancel"),
        "try_again": _("Try again"),
    }


def is_selected(data: dict, widget: Whenable, manager: DialogManager):
    if manager.find("m_field").get_checked():
        return True
    return False


async def edit_project_selected(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    data: str = None,
):
    is_favorite_button = button.widget_id
    if is_favorite_button == "True" or is_favorite_button == "False":
        manager.dialog_data["starred"] = is_favorite_button

    fields_states_map = {
        "1": EditProjectSG.name,
        "2": EditProjectSG.key,
        "3": EditProjectSG.starred
    }
    mselect_widget = manager.find("m_field")
    selected_fields = sorted(mselect_widget.get_checked())

    if len(selected_fields):
        await manager.switch_to(fields_states_map[selected_fields[0]])
        await mselect_widget.set_checked(selected_fields[0], False)
    else:
        await edit_project(manager)


async def edit_project(manager: DialogManager):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    redis: Redis = manager.middleware_data["redis"]
    session: ClientSession = manager.middleware_data["session"]

    project_id = manager.start_data
    headers = await get_headers(
        user_id=manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis,
    )

    key = manager.find("key").get_value()
    values = [
        ("name", manager.find("name").get_value()),
        ("key", key.upper() if key else None),
        ("starred", manager.dialog_data.get("starred"))
    ]

    results = await Project().edit_item(
        session=session,
        id=project_id,
        headers=headers,
        data={k: v for k, v in values if v is not None}
    )

    if "error_name" in results:
        manager.dialog_data["error_name"] = results["error_name"]
        return await manager.switch_to(EditProjectSG.name)
    elif "error_key" in results:
        manager.dialog_data["error_key"] = results["error_key"]
        return await manager.switch_to(EditProjectSG.key)
    elif "error" in results:
        return await manager.switch_to(EditProjectSG.name)
    await manager.done(results["success"])


async def delete_project(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    redis: Redis = manager.middleware_data["redis"]
    session: ClientSession = manager.middleware_data["session"]

    project_id = manager.start_data
    headers = await get_headers(
        user_id=manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    result = await Project.delete_item(session, project_id, headers)

    if "success" in result:
        return await manager.done(result["success"])
    manager.dialog_data["error"] = result["error"]


async def issues_texts(*args, **kwargs):
    return {
        "issues_text": _("Your issues:"),
        "zero_issues": _("You don't have issues yet."),
        "back": _("Back"),
        "cancel": _("Cancel"),
        "create": _("Create new"),
        "title_text": _("Enter issue title:"),
        "description_text": _("Enter description of issue:"),
        "type_text": _("Is this project will be a favorite:"),
        "priority_text": _("Is this project will be a favorite:"),
    }


async def create_issue_texts(*args, **kwargs):
    return {
        "cancel": _("Cancel"),
        "skip": _("Skip"),
        "title_text": _("Enter issue title:"),
        "description_text": _("Enter description of issue:"),
        "type_text": _("Select the issue type:"),
        "types": [(_("Feature"), "Feature"), (_("Bug"), "Bug")],
        "priority_text": _(
            "Select the priority of the issue. "
            "\nDefault is <b>Medium</b>:"
        ),
        "prioritys": [
            (_("Lowest"), "Lowest"),
            (_("Low"), "Low"),
            (_("Medium"), "Medium"),
            (_("High"), "High"),
            (_("Highest"), "Highest"),
        ],
        "status_text": _("Select the issue status. \nDefault is <b>To do</b>:"),
        "statuses": [
            (_("To do"), "To do"),
            (_("In progress"), "In progress"),
            (_("Done"), "Done"),
        ],
    }


async def issues_getter(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    project_id = dialog_manager.start_data

    if headers is not None:
        # Limit in 9999 projects (default is 10)
        # is necessary to get pagination working.
        issues = await Issue.get_items(session, headers, project_id, {"limit": 9999})

        if "count" in issues:
            return {"issues": issues["results"]}
        return {"no_issues": issues["detail"]}


async def create_issue(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    redis: Redis = manager.middleware_data["redis"]
    session: ClientSession = manager.middleware_data["session"]

    headers = await get_headers(
        user_id=manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis,
    )
    issue_data = {
        "title": manager.find("title").get_value(),
        "type": manager.dialog_data["type"],
        "priority": manager.dialog_data.get("priority") or "Medium",
        "status": manager.dialog_data.get("status") or "To do",
    }

    if description := manager.find("description").get_value():
        issue_data["description"] = description

    results = await Issue().create_item(
        session=session,
        headers=headers,
        project_id=manager.start_data,
        data=issue_data
    )

    if "error_title" in results:
        manager.dialog_data["error_title"] = results["error_title"]
        return await manager.switch_to(CreateIssueSG.title)
    elif "error" in results:
        manager.dialog_data["error"] = results["error"]
        return await manager.switch_to(CreateIssueSG.title)

    await manager.done(results["success"])


async def issue_texts(*args, **kwargs):
    return {
        "issues": _("Issues"),
        "edit": _("Edit"),
        "delete": _("Delete"),
        "back": _("Back")
    }


async def issue_getter(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    project_id, issue_id = dialog_manager.start_data
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    lang, tz = await get_lang_and_tz(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    issue = await Issue.get_item(
        session=session,
        id=issue_id,
        project_id=project_id,
        headers=headers,
        language=lang,
        timezone=tz
    )
    issue_type, priority, status = Issue.get_translated_fields(issue)

    formatted_issue = _(
        """\
            \n<b>Title</b>: {title}\
            \n<b>Description</b>: {description}\
            \n<b>Type</b>: {type}\
            \n<b>Priority</b>: {priority}\
            \n<b>Status</b>: {status}\
            \n<b>Created</b>: {created}\
            \n<b>Updated</b>: {updated}
        """
    ).format(
        title=issue["title"],
        description=issue["description"],
        type=issue_type,
        priority=priority,
        status=status,
        created=issue["created"],
        updated=issue["updated"]
    )

    return {"issue": formatted_issue}


async def clicked_edit_issue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(EditIssueSG.select, dialog_manager.start_data)


async def issue_edit_texts(*args, **kwargs):
    return {
        "instructions": _("Select what you want to change:"),
        "continue": _("Continue"),
        "cancel": _("Cancel"),
        "skip": _("Skip"),
        "title_text": _("Enter issue title:"),
        "description_text": _("Enter description of issue:"),
        "fields": [
            (_("Title"), "1"),
            (_("Description"), "2"),
            (_("Type"), "3"),
            (_("Priority"), "4"),
            (_("Status"), "5"),
        ],
        "type_text": _("Select the issue type:"),
        "types": [(_("Feature"), "Feature"), (_("Bug"), "Bug")],
        "priority_text": _("Select the priority of the issue."),
        "prioritys": [
            (_("Lowest"), "Lowest"),
            (_("Low"), "Low"),
            (_("Medium"), "Medium"),
            (_("High"), "High"),
            (_("Highest"), "Highest"),
        ],
        "status_text": _("Select the issue status."),
        "statuses": [
            (_("To do"), "To do"),
            (_("In progress"), "In progress"),
            (_("Done"), "Done"),
        ],
    }


async def edit_issue_selected(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    data: str = None,
):
    if button.widget_id != "confirm_select":
        manager.dialog_data[button.widget_id] = data

    fields_states_map = {
        "1": EditIssueSG.title,
        "2": EditIssueSG.description,
        "3": EditIssueSG.type,
        "4": EditIssueSG.priority,
        "5": EditIssueSG.status,
    }
    mselect_widget = manager.find("m_field")
    selected_fields = sorted(mselect_widget.get_checked())

    if len(selected_fields):
        await manager.switch_to(fields_states_map[selected_fields[0]])
        await mselect_widget.set_checked(selected_fields[0], False)
    else:
        await edit_issue(manager)


async def edit_issue(manager: DialogManager):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    redis: Redis = manager.middleware_data["redis"]
    session: ClientSession = manager.middleware_data["session"]

    project_id, issue_id = manager.start_data
    headers = await get_headers(
        user_id=manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis,
    )

    values = [
        ("title", manager.dialog_data.get("title")),
        ("description", manager.dialog_data.get("description")),
        ("type", manager.dialog_data.get("type")),
        ("priority", manager.dialog_data.get("priority")),
        ("status", manager.dialog_data.get("status"))
    ]

    results = await Issue().edit_item(
        session=session,
        id=issue_id,
        headers=headers,
        project_id=project_id,
        data={k: v for k, v in values if v is not None},
    )

    if "error_title" in results:
        manager.dialog_data["error_title"] = results["error_title"]
        return await manager.switch_to(EditIssueSG.title)
    elif "error" in results:
        manager.dialog_data["error"] = results["error"]
        return await manager.switch_to(EditIssueSG.title)
    await manager.done(results["success"])


async def delete_issue(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    sessionmaker: async_sessionmaker = manager.middleware_data["sessionmaker"]
    redis: Redis = manager.middleware_data["redis"]
    session: ClientSession = manager.middleware_data["session"]

    project_id, issue_id = manager.start_data
    headers = await get_headers(
        user_id=manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    result = await Issue.delete_item(session, issue_id, project_id, headers)

    if "success" in result:
        return await manager.done(result["success"])
    manager.dialog_data["error"] = result["error"]
