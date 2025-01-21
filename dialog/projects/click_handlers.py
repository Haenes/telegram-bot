from aiogram.types import CallbackQuery, Message

from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from .states import CreateProjectSG, ProjectSG, EditProjectSG
from dialog.utils import get_headers
from dialog.bugtracker_api import Project


async def new_dialog_project(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(ProjectSG.details, dialog_manager.item_id)


async def create_project_input(
    message: Message,
    text: ManagedTextInput,
    manager: DialogManager,
    input: str
):
    input_id = text.widget.widget_id

    manager.show_mode = ShowMode.EDIT
    manager.dialog_data[input_id] = input
    await message.delete()

    if input_id == "name" and "error_name" in manager.dialog_data:
        del manager.dialog_data["error_name"]
        return await create_project(message, text, manager)
    elif input_id == "key" and "error_key" in manager.dialog_data:
        del manager.dialog_data["error_key"]
        return await create_project(message, text, manager)
    await manager.next()


async def create_project_starred(
    callback: CallbackQuery,
    select: Select,
    manager: DialogManager,
    starred: bool
):
    manager.dialog_data["starred"] = starred
    await create_project(callback, select, manager)


async def create_project(
    event: CallbackQuery | Message,
    source: Button | ManagedTextInput | Select,
    dialog_manager: DialogManager,
):
    sessionmaker: async_sessionmaker = dialog_manager.middleware_data["sessionmaker"]
    redis: Redis = dialog_manager.middleware_data["redis"]
    session: ClientSession = dialog_manager.middleware_data["session"]

    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis,
    )
    data = {
        "name": dialog_manager.dialog_data["name"],
        "key": dialog_manager.dialog_data["key"].upper(),
        "starred": dialog_manager.dialog_data["starred"],
    }
    results = await Project().create_item(session, headers, data)

    if "error_name" in results:
        dialog_manager.dialog_data["error_name"] = results["error_name"]
        return await dialog_manager.switch_to(CreateProjectSG.name)
    elif "error_key" in results:
        dialog_manager.dialog_data["error_key"] = results["error_key"]
        return await dialog_manager.switch_to(CreateProjectSG.key)
    elif "error" in results:
        dialog_manager.dialog_data["error"] = results["error"]
        return await dialog_manager.switch_to(CreateProjectSG.name)
    await dialog_manager.done(results["success"])


async def new_dialog_edit_project(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(EditProjectSG.select, dialog_manager.start_data)


async def edit_project_selected(
    event: CallbackQuery | Message,
    source: Button | ManagedTextInput | Select,
    manager: DialogManager,
    data: str | bool = None,
):
    if source.widget_id != "confirm_select":
        manager.dialog_data[source.widget_id] = data

    fields_states_map = {
        "1": EditProjectSG.name,
        "2": EditProjectSG.key,
        "3": EditProjectSG.starred
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

    key = manager.dialog_data.get("key")
    values = [
        ("name", manager.dialog_data.get("name")),
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
