from aiogram import Router, types, F

from handlers.bugtracker_api import set_up, Paginator
from keyboards.for_issues import issues_kb


router = Router()


@router.callback_query(F.data.startswith("next_issues_"), F.data.as_("data"))
async def next_issues(callback: types.CallbackQuery, data: types.CallbackQuery):
    page = data.removeprefix("next_issues_")

    headers = set_up()
    paginator = Paginator(headers, page)
    results = paginator.next_issues()

    await callback.message.answer(f"List of issues, page {page}:", reply_markup=issues_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("back_issues_"), F.data.as_("data"))
async def back_issues(callback: types.CallbackQuery, data: types.CallbackQuery):
    page = data.removeprefix("back_issues_")

    headers = set_up()
    paginator = Paginator(headers, page)
    results = paginator.previous_issues()

    await callback.message.answer(f"List of issues, page {page}:", reply_markup=issues_kb(results))
    await callback.answer()
