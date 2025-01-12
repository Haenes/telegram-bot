from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from aiohttp import ClientSession

from handlers.bugtracker_api import Issue
from keyboards.for_issues import issues_kb


router = Router()


@router.callback_query(
    F.data.startswith("next_issues_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def next_issues(
    callback: CallbackQuery,
    data: str,
    user_headers: dict,
    session: ClientSession
):
    project_id, page = data.split("_")[2:]
    results = await Issue().pagination_next(
        session,
        user_headers,
        project_id,
        page
    )

    await callback.message.answer(
        _("List of issues, page {page}:").format(page=page),
        reply_markup=issues_kb(results)
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("prev_issues_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def prev_issues(
    callback: CallbackQuery,
    data: str,
    user_headers: dict,
    session: ClientSession
):
    project_id, page = data.split("_")[2:]
    results = await Issue().pagination_back(
        session,
        user_headers,
        project_id,
        page
    )

    await callback.message.answer(
        _("List of issues, page {page}:").format(page=page),
        reply_markup=issues_kb(results)
    )
    await callback.answer()
