from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Translate, get_issue, update_issue
from handlers.common import clear_state_and_save_data
from keyboards.for_issues import (
    issue_type_kb,
    issue_priority_kb,
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
    F.data.startswith("change_issue_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def change_update(
    callback: CallbackQuery,
    state: FSMContext,
    data: str,
    user_headers: dict
):
    # It is necessary to fill in issue data once and take them from it,
    # instead of calling a "get_issue" function in each handler to get data
    global issue_data

    project_id, issue_id = data.split("_")[2:]
    issue_data = await get_issue(issue_id, project_id, user_headers)

    text = _(
        """
            Now you will need to enter the data one by one to update issue.\
            \n<u>Note</u>: you can cancel the update process by command:  /cancel.
            \n<b>Previous title: {title}</b>\
            \n<b>New title:</b>
        """
    ).format(title=issue_data['title'])

    await callback.message.answer(text)
    await state.set_state(UpdateIssue.title)
    await callback.answer()


@router.message(UpdateIssue.title)
async def title_enter(message: Message, state: FSMContext):
    # Set a project without the user's input.
    await state.update_data(project=issue_data["project_id"])
    await state.update_data(title=message.text)

    text = _(
        """
            Good, now enter the issue description.
            \n<b>Previous description: {description}</b>\
            \n<b>New description:</b>
        """
    ).format(description=issue_data['description'])

    await message.answer(text)
    await state.set_state(UpdateIssue.description)


@router.message(UpdateIssue.description)
async def description_enter(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    type = Translate(issue_data).issue()[0]

    text = _(
        """
            Good, now select the issue type.
            \n<b>Previous type: {type}</b>\
            \n<b>New type:</b>
        """
    ).format(type=type)

    await message.answer(text, reply_markup=issue_type_kb())
    await state.set_state(UpdateIssue.type)


@router.callback_query(
    UpdateIssue.type,
    F.data.startswith("iss_type_"),
    F.data.as_("data")
)
async def type_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext
):
    await state.update_data(type=data.removeprefix("iss_type_"))

    priority = Translate(issue_data).issue()[1]

    text = _(
        """
            Good, now select the issue priority
            \n<b>Previous priority: {priority}</b>\
            \n<b>New priority:</b>
        """
    ).format(priority=priority)

    await callback.message.answer(text, reply_markup=issue_priority_kb())
    await callback.answer()
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
    F.data.as_("data")
)
async def priority_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext
):
    await state.update_data(priority=data.removeprefix("iss_priority_"))

    status = Translate(issue_data).issue()[2]

    text = _(
        """
            Good, now select the issue status.
            \n<b>Previous status: {status}</b>\
            \n<b>New status:</b>
        """
    ).format(status=status)

    await callback.message.answer(text, reply_markup=issue_status_kb())
    await callback.answer()
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
    flags={"set_headers": "set_headers"}
)
async def status_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext,
    user_headers: dict
):
    data = data.removeprefix("iss_status_")

    if data != "Done":
        status = data[:2] + "" + data[2:]
    else:
        status = data

    await state.update_data(status=status)
    user_data = await state.get_data()
    results = await update_issue(
        issue_data["id"],
        issue_data["project_id"],
        user_data,
        user_headers
    )

    await callback.message.answer(results)
    await callback.answer()
    await clear_state_and_save_data(state)


@router.message(UpdateIssue.status)
async def status_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=issue_status_kb()
    )
