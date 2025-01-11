from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Paginator
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
    user_headers: dict
):
    project_id, page = data.split("_")[2:]
    results = await Paginator(user_headers, page).next_issues(project_id)

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
    user_headers: dict
):
    project_id, page = data.split("_")[2:]
    results = await Paginator(user_headers, page).previous_issues(project_id)

    await callback.message.answer(
        _("List of issues, page {page}:").format(page=page),
        reply_markup=issues_kb(results)
    )
    await callback.answer()
