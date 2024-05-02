from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Translate, main
from keyboards.for_issues import issues_kb, issue_kb


router = Router()


@router.callback_query(
        F.data == "issues",
        flags={"set_headers": "set_headers"})
async def send_issues(callback: types.CallbackQuery, user_headers):
    if user_headers is not None:
        results = await main(endpoint="get_issues", headers=user_headers)

        await callback.message.answer(
            _("List of issues, page 1:"),
            reply_markup=issues_kb(results)
            )
    else:
        await callback.message.answer(
            _("You aren't logged in, use /login command.")
        )
    await callback.answer()


@router.callback_query(
        F.data.startswith("issue_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers", "lang_tz": "lang_tz"})
async def send_issue(
        callback: types.CallbackQuery,
        data, user_headers,
        language, timezone):
    issue_id = data.removeprefix("issue_")

    results = await main(
        endpoint="get_issue",
        id=issue_id,
        headers=user_headers,
        language=language,
        timezone=timezone
    )

    issue_type, priority, status = Translate(results).issue()

    text = _("""
<b>Project</b>: {project}
<b>Title</b>: {title}
<b>Description</b>: {description}
<b>Key</b>: {key}
<b>Type</b>: {type}
<b>Priority</b>: {priority}
<b>Status</b>: {status}
<b>Created</b>: {created}
<b>Updated</b>: {updated}
            """).format(project=results['project'], title=results['title'],
                        description=results['description'], key=results['key'],
                        type=issue_type, priority=priority, status=status,
                        created=results['created'], updated=results['updated']
                        )

    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=issue_kb(results)
        )
    await callback.answer()


@router.callback_query(
        F.data.startswith("iss_delete_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers"})
async def del_issue(callback: types.CallbackQuery, data, user_headers):
    issue_id = data.removeprefix("iss_delete_")

    results = await main(
        endpoint="delete_issue",
        id=issue_id,
        headers=user_headers
    )

    await callback.message.answer(results)
    await callback.answer()
