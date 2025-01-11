from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import (
    Translate,
    get_issues,
    get_issue,
    delete_issue
)
from keyboards.for_issues import issues_kb, issue_kb


router = Router()


@router.callback_query(
    F.data.startswith("issues_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def send_issues(
    callback: CallbackQuery,
    user_headers: dict,
    data: str
):
    project_id = data.removeprefix("issues_")

    if user_headers is not None:
        results = await get_issues(user_headers, project_id)

        if "count" in results:
            await callback.message.answer(
                _("List of issues, page 1:"),
                reply_markup=issues_kb(results)
            )
            return await callback.answer()

        await callback.message.answer(
            (results),
            reply_markup=issues_kb(project_id)
        )
    else:
        await callback.message.answer(
            _("You aren't logged in, use /login command.")
        )
    await callback.answer()


@router.callback_query(
    F.data.startswith("issue_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers", "lang_tz": "lang_tz"}
)
async def send_issue(
    callback: CallbackQuery,
    data: str,
    user_headers: dict,
    language: str,
    timezone: str
):
    project_id, issue_id = data.split("_")[1:]
    results = await get_issue(
        issue_id,
        project_id,
        user_headers,
        language=language,
        timezone=timezone
    )

    issue_type, priority, status = Translate(results).issue()

    text = _(
        """
            <b>Title</b>: {title}\
            \n<b>Description</b>: {description}\
            \n<b>Type</b>: {type}\
            \n<b>Priority</b>: {priority}\
            \n<b>Status</b>: {status}\
            \n<b>Created</b>: {created}\
            \n<b>Updated</b>: {updated}
        """
    ).format(
        title=results["title"],
        description=results["description"],
        type=issue_type,
        priority=priority,
        status=status,
        created=results["created"],
        updated=results["updated"]
    )

    await callback.message.answer(text, reply_markup=issue_kb(results))
    await callback.answer()


@router.callback_query(
    F.data.startswith("delete_issue_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def del_issue(
    callback: CallbackQuery,
    data: str,
    user_headers: dict
):
    project_id, issue_id = data.split("_")[2:]
    results = await delete_issue(issue_id, project_id, user_headers)

    await callback.message.answer(results)
    await callback.answer()
