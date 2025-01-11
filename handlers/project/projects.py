from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import (
    Translate,
    get_projects,
    get_project,
    delete_project
)
from keyboards.for_projects import projects_kb, project_kb


router = Router()


@router.message(
    Command("projects"),
    flags={"set_headers": "set_headers"}
)
async def cmd_projects(message: Message, user_headers: dict):
    if user_headers is not None:
        results = await get_projects(headers=user_headers)

        if "count" in results:
            return await message.answer(
                _("List of projects, page 1:"),
                reply_markup=projects_kb(results)
            )

        await message.answer((results), reply_markup=projects_kb(results))
    else:
        await message.answer(
            _("You aren't logged in, use /login command.")
        )


@router.callback_query(
    F.data.startswith("project_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers", "lang_tz": "lang_tz"}
)
async def send_project(
    callback: CallbackQuery,
    data: str,
    user_headers: dict,
    language: str,
    timezone: str
):
    project_id = data.removeprefix("project_")
    results = await get_project(
        id=project_id,
        headers=user_headers,
        language=language,
        timezone=timezone
    )

    starred = Translate(results).project()
    text = _(
        """
            <b>Name</b>: {name} \
            \n<b>Key</b>: {key} \
            \n<b>Favorite</b>: {starred} \
            \n<b>Created</b>: {created} \
            \n<b>Updated</b>: {updated}
        """
    ).format(
        name=results['name'],
        key=results['key'],
        starred=starred,
        created=results['created'],
        updated=results['updated']
    )

    await callback.message.answer(text, reply_markup=project_kb(results))
    await callback.answer()


@router.callback_query(
    F.data.startswith("prj_delete_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def del_project(
    callback: CallbackQuery,
    data: str,
    user_headers: dict
):
    project_id = data.removeprefix("prj_delete_")
    results = await delete_project(id=project_id, headers=user_headers)

    await callback.message.answer(results)
    await callback.answer()
