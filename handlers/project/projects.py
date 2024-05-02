from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Translate, main
from keyboards.for_projects import projects_kb, project_kb


router = Router()


@router.callback_query(
        F.data == "projects",
        flags={"set_headers": "set_headers"})
async def send_projects(callback: types.CallbackQuery, user_headers):
    if user_headers is not None:
        results = await main(endpoint="get_projects", headers=user_headers)

        await callback.message.answer(
            _("List of projects, <b>page 1</b>:"),
            parse_mode="HTML",
            reply_markup=projects_kb(results)
            )
    else:
        await callback.message.answer(
            _("You aren't logged in, use /login command.")
            )
    await callback.answer()


@router.callback_query(
        F.data.startswith("project_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers", "lang_tz": "lang_tz"})
async def send_project(
        callback: types.CallbackQuery,
        data: types.CallbackQuery,
        user_headers, language, timezone):
    project_id = data.removeprefix("project_")
    results = await main(
        endpoint="get_project",
        id=project_id,
        headers=user_headers,
        language=language,
        timezone=timezone
        )

    starred = Translate(results).project()

    text = _("""
<b>Name</b>: {name}
<b>Description</b>: {description}
<b>Key</b>: {key}
<b>Type</b>: {type}
<b>Favorite</b>: {starred}
<b>Created</b>: {created}
            """).format(name=results['name'],
                        description=results['description'],
                        key=results['key'], type=results['type'],
                        starred=starred, created=results['created']
                        )

    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=project_kb(results)
        )
    await callback.answer()


@router.callback_query(
        F.data.startswith("prj_delete_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers"})
async def del_project(callback: types.CallbackQuery, data, user_headers):
    project_id = data.removeprefix("prj_delete_")
    results = await main(
        endpoint="delete_project",
        id=project_id,
        headers=user_headers
        )

    await callback.message.answer(results)
    await callback.answer()
