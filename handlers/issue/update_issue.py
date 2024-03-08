from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Translate, get_issue, update_issue
from keyboards.for_issues import (
    issue_type_kb, issue_priority_kb,
    issue_status_kb
    )


router = Router()


class UpdateIssue(StatesGroup):
    title = State()
    description = State()
    type = State()
    priority = State()
    status = State()


issue_data = {}


@router.callback_query(
        F.data.startswith("iss_change_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers"})
async def change_update(
        callback: types.CallbackQuery,
        state: FSMContext,
        data: types.CallbackQuery,
        user_headers):
    # It is necessary to fill in issue data once and take them from it,
    # instead of calling a "get_issue" function in each handler to get data
    global issue_data

    issue_id = data.removeprefix("iss_change_")
    issue_data = get_issue(issue_id, user_headers)

    text = _("""
Now you will need to enter the data one by one to update issue.
<u>Note</u>: you can cancel the update process by entering: /cancel. \n
<b>Previous title: {title}</b>
<b>New title:</b>
            """).format(title=issue_data['title'])

    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateIssue.title)
    await callback.answer()


@router.message(UpdateIssue.title)
async def title_enter(message: types.Message, state: FSMContext):
    # Set a project and key without the user's input
    await state.update_data(project=issue_data["project"])
    await state.update_data(key=issue_data["key"])
    await state.update_data(title=message.text)

    text = _("""
Good, now enter the issue description. \n
<b>Previous description: {description}</b>
<b>New description:</b>
            """).format(description=issue_data['description'])

    await message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateIssue.description)


@router.message(UpdateIssue.description)
async def description_enter(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    type = Translate(issue_data).issue()[0]

    text = _("""
Good, now select the issue type. \n
<b>Previous type: {type}</b>
<b>New type:</b>
            """).format(type=type)

    await message.answer(text, parse_mode="HTML", reply_markup=issue_type_kb())
    await state.set_state(UpdateIssue.type)


@router.callback_query(
        UpdateIssue.type,
        F.data.startswith("iss_type_"),
        F.data.as_("data"))
async def type_selected(
        callback: types.CallbackQuery,
        data: types.CallbackQuery,
        state: FSMContext):
    await state.update_data(type=data.removeprefix("iss_type_"))

    priority = Translate(issue_data).issue()[1]

    text = _("""
Good, now select the issue priority \n
<b>Previous priority: {priority}</b>
<b>New priority:</b>
            """).format(priority=priority)

    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=issue_priority_kb()
        )
    await state.set_state(UpdateIssue.priority)


@router.message(UpdateIssue.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=issue_type_kb()
        )


@router.callback_query(
        UpdateIssue.priority,
        F.data.startswith("iss_priority_"),
        F.data.as_("data"))
async def priority_selected(
        callback: types.CallbackQuery,
        data: types.CallbackQuery,
        state: FSMContext):
    await state.update_data(priority=data.removeprefix("iss_priority_"))

    status = Translate(issue_data).issue()[2]

    text = _("""
Good, now select the issue status. \n
<b>Previous status: {status}</b>
<b>New status:</b>
            """).format(status=status)

    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=issue_status_kb()
        )
    await state.set_state(UpdateIssue.status)


@router.message(UpdateIssue.priority)
async def priority_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=issue_priority_kb()
        )


@router.callback_query(
        UpdateIssue.status,
        F.data.startswith("iss_status_"),
        F.data.as_("data"),
        flags={"set_headers": "set_headers"})
async def status_selected(
        callback: types.CallbackQuery,
        data: types.CallbackQuery,
        state: FSMContext, user_headers):
    data = data.removeprefix("iss_status_")

    if data != "Done":
        status = data[:2] + "" + data[2:]
    else:
        status = data

    await state.update_data(status=status)
    user_data = await state.get_data()

    result = update_issue(issue_data["id"], user_data, user_headers)

    if result == 200:
        await callback.message.answer(
            _("The issue has been successfully updated!")
            )
        callback.answer()
    else:
        await callback.message.answer(
            _("An error occurred, the issue was NOT updated!")
            )
        callback.answer()

    await state.clear()


@router.message(UpdateIssue.status)
async def status_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=issue_status_kb()
        )
