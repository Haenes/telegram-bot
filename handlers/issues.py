import os

from aiogram import Router, types, F

from handlers.bugtracker_api import get_issues, get_issue
from keyboards.for_issues import issues_kb


router = Router()


@router.callback_query(F.data == "issues")
async def send_issues(callback: types.CallbackQuery):
    token = os.environ.get("API_TOKEN")
    HEADERS = {"Authorization": f"Token {token}"}

    results = get_issues(HEADERS)
    # print(results)

    await callback.message.answer("List of issues:", reply_markup=issues_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("issue"), F.data.as_("data"))
async def send_issue(callback: types.CallbackQuery, data):
    token = os.environ.get("API_TOKEN")
    HEADERS = {"Authorization": f"Token {token}"}

    issue_id = data.removeprefix("issue_")
    results = get_issue(issue_id, HEADERS)
    # print(results)

    await callback.message.answer(f"Title: {results['title']} \nDescription: {results['description']} \nKey: {results['key']} \nType: {results['type']} \nPriority: {results['priority']} \nStatus: {results['status']} \nCreated: {results['created']} \nUpdated: {results['updated']}")
    await callback.answer()
