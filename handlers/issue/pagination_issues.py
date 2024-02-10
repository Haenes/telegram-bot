from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Paginator
from keyboards.for_issues import issues_kb


router = Router()


@router.callback_query(
        F.data.startswith("next_issues_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers"})
async def next_issues(
        callback: types.CallbackQuery,
        data: types.CallbackQuery,
        user_headers):
    page = data.removeprefix("next_issues_")
    paginator = Paginator(user_headers, page)
    results = paginator.next_issues()

    await callback.message.answer(
        _("List of issues, page {page}:").format(page=page),
        reply_markup=issues_kb(results)
        )
    await callback.answer()


@router.callback_query(
        F.data.startswith("back_issues_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers"})
async def back_issues(
        callback: types.CallbackQuery,
        data: types.CallbackQuery,
        user_headers):
    page = data.removeprefix("back_issues_")

    paginator = Paginator(user_headers, page)
    results = paginator.previous_issues()

    await callback.message.answer(
        _("List of issues, page {page}:").format(page=page),
        reply_markup=issues_kb(results)
        )
    await callback.answer()
