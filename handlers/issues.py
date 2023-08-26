from aiogram import Router, types, F

from handlers.bugtracker_api import set_up, get_issues, get_issue, delete_issue
from keyboards.for_issues import issues_kb, issue_kb


router = Router()


@router.callback_query(F.data == "issues")
async def send_issues(callback: types.CallbackQuery):
    headers = set_up()
    results = get_issues(headers)

    await callback.message.answer("List of issues, page 1:", reply_markup=issues_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("issue_"), F.data.as_("data"))
async def send_issue(callback: types.CallbackQuery, data):
    issue_id = data.removeprefix("issue_")
    headers = set_up()
    results = get_issue(issue_id, headers)

    await callback.message.answer(f"Title: {results['title']} \nDescription: {results['description']} \nKey: {results['key']} \nType: {results['type']} \nPriority: {results['priority']} \nStatus: {results['status']} \nCreated: {results['created']} \nUpdated: {results['updated']}", reply_markup=issue_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("iss_delete_"), F.data.as_("data"))
async def del_issue(callback: types.CallbackQuery, data):
    headers = set_up()
    issue_id = data.removeprefix("iss_delete_")
    results = delete_issue(issue_id, headers)

    await callback.message.answer(results)
    await callback.answer()
