from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from aiohttp import ClientSession

from handlers.bugtracker_api import Issue
from handlers.common import clear_state_and_save_data
from keyboards.for_issues import (
    issue_type_kb,
    issue_priority_kb,
)

router = Router()


class CreateIssue(StatesGroup):
    project_id = State()
    title = State()
    description = State()
    type = State()
    priority = State()


@router.callback_query(F.data.startswith("create_issue_"), F.data.as_("data"))
async def create_issue(
    callback: CallbackQuery,
    state: FSMContext,
    data: str
):
    await state.update_data(project_id=data.removeprefix("create_issue_"))

    text = _(
        """
            Now you will need to enter the data one by one to create a new issue.\
            \n<u>Note</u>: you can cancel the creation process by command:  /cancel.
            \n<b>Enter the issue title:</b>
        """
    )

    await callback.message.answer(text)
    await state.set_state(CreateIssue.title)
    await callback.answer()


@router.message(CreateIssue.title)
async def title_enter(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(_("Good, now <b>enter description:</b>"))
    await state.set_state(CreateIssue.description)


@router.message(CreateIssue.description)
async def description_enter(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        _("Good, now <b>select type:</b>"),
        reply_markup=issue_type_kb()
    )
    await state.set_state(CreateIssue.type)


@router.callback_query(
    CreateIssue.type,
    F.data.startswith("iss_type_"),
    F.data.as_("data")
)
async def type_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext
):
    await state.update_data(type=data.removeprefix("iss_type_"))
    await callback.message.answer(
        _("Good, now <b>select priority:</b>"),
        reply_markup=issue_priority_kb()
    )
    await callback.answer()
    await state.set_state(CreateIssue.priority)


@router.message(CreateIssue.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=issue_type_kb()
    )


@router.callback_query(
    CreateIssue.priority,
    F.data.startswith("iss_priority_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def priority_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext,
    user_headers: dict,
    session: ClientSession
):
    await state.update_data(priority=data.removeprefix("iss_priority_"))

    user_data = await state.get_data()
    project_id = user_data["project_id"]
    # results = await make_issue(user_data, project_id, user_headers)
    results = await Issue().create_item(
        session,
        user_data,
        project_id,
        user_headers
    )

    await callback.message.answer(results)
    await callback.answer()
    await clear_state_and_save_data(state)


@router.message(CreateIssue.priority)
async def priority_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=issue_priority_kb()
    )
