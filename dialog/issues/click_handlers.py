from aiogram.types import CallbackQuery, Message

from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from .states import IssuesSG, IssueSG, CreateIssueSG, EditIssueSG
from dialog.utils import get_headers
from dialog.bugtracker_api import Issue


async def new_dialog_issues(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(IssuesSG.main, dialog_manager.start_data)


async def new_dialog_issue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    # Pass project_id and issue_id.
    start_data = dialog_manager.start_data, dialog_manager.item_id
    await dialog_manager.start(IssueSG.details, start_data)


async def new_dialog_create_issue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(CreateIssueSG.title, dialog_manager.start_data)


async def create_issue_input(
    message: Message,
    text: ManagedTextInput,
    manager: DialogManager,
    input: str
):
    input_id = text.widget.widget_id

    manager.show_mode = ShowMode.EDIT
    manager.dialog_data[input_id] = input
    await message.delete()

    if input_id == "title" and "error_title" in manager.dialog_data:
        del manager.dialog_data["error_title"]
        return await create_issue(message, text, manager)
    await manager.next()


async def create_issue_selected(
    callback: CallbackQuery,
    select: Select,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data[select.widget_id] = data

    if select.widget_id == "status":
        return await create_issue(callback, select, dialog_manager)
    await dialog_manager.next()


async def create_issue(
    event: CallbackQuery | Message,
    source: Button | Select,
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
        "title": manager.dialog_data["title"],
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


async def new_dialog_edit_issue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(EditIssueSG.select, dialog_manager.start_data)


async def edit_issue_selected(
    event: CallbackQuery | Message,
    source: Button | ManagedTextInput | Select,
    manager: DialogManager,
    data: str = None
):
    if source.widget_id != "confirm_select":
        manager.dialog_data[source.widget_id] = data

    fields_states_map = {
        "1": EditIssueSG.title,
        "2": EditIssueSG.description,
        "3": EditIssueSG.type,
        "4": EditIssueSG.priority,
        "5": EditIssueSG.status,
    }
    mselect_widget = manager.find("m_field")
    selected_fields = sorted(mselect_widget.get_checked())

    if type(event) is Message:
        manager.show_mode = ShowMode.EDIT
        await manager.event.delete()

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
