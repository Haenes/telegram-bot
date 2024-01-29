from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import convert_project_to_url, make_issue
from keyboards.for_issues import issue_type_kb, issue_priority_kb, issue_status_kb


router = Router()


class CreateIssue(StatesGroup):
    project = State()
    title = State()
    description = State()
    key = State()
    type = State()
    priority = State()
    status = State()


@router.callback_query(F.data == "create_issue")
async def create_issue(callback: types.CallbackQuery, state: FSMContext):

    text = _("""
Now you will need to enter the data one by one to create a new issue. 
<u>Note</u>: you can cancel the creation process by entering: /cancel. \n
<b>Enter related to issue project:</b>
            """)

    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(CreateIssue.project)
    await callback.answer()


#TODO ИЗМЕНИТЬ all_projects(), ДОБАВИВ В КАЧЕСТВЕ АРГУМЕНТА HEADERS И ПЕРЕДОВАТЬ ИХ
@router.message(CreateIssue.project, flags={"set_headers":"set_headers"})
async def project_enter(message: types.Message, state: FSMContext, user_headers):
    project = convert_project_to_url(user_headers, message.text)

    if project == "UnboundLocalError":
        await message.answer(_("Project not found! Please, try again!"))
    else: 
        await state.update_data(project=project)  
        await message.answer(_("Good, now <b>enter the issue title:</b>"), parse_mode="HTML")
        await state.set_state(CreateIssue.title)


@router.message(CreateIssue.project)
async def project_enter_incorrect(message: types.Message, state: FSMContext):
    await message.answer(_("Invalid project name, please, try again!"))


@router.message(CreateIssue.title)
async def title_enter(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(_("Good, now <b>enter description:</b>"), parse_mode="HTML")
    await state.set_state(CreateIssue.description)


@router.message(CreateIssue.description)
async def description_enter(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(_("Good, now <b>enter key:</b>"), parse_mode="HTML")
    await state.set_state(CreateIssue.key)


@router.message(CreateIssue.key)
async def key_enter(message: types.Message, state: FSMContext):
    await state.update_data(key=message.text)
    await message.answer(_("Good, now <b>select type:</b>"), parse_mode="HTML", reply_markup=issue_type_kb())
    await state.set_state(CreateIssue.type)


@router.callback_query(CreateIssue.type, F.data.startswith("iss_type_"), F.data.as_("data"))
async def type_selected(callback: types.CallbackQuery, data: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=data.removeprefix("iss_type_"))
    await callback.message.answer(_("Good, now <b>select priority:</b>"), parse_mode="HTML", reply_markup=issue_priority_kb())
    await state.set_state(CreateIssue.priority)


@router.message(CreateIssue.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(_("Please select one of the options on the keyboard."), reply_markup=issue_type_kb())


@router.callback_query(CreateIssue.priority, F.data.startswith("iss_priority_"), F.data.as_("data"))
async def priority_selected(callback: types.CallbackQuery, data: types.CallbackQuery, state: FSMContext):
    await state.update_data(priority=data.removeprefix("iss_priority_"))
    await callback.message.answer(_("Good, now <b>select status:</b>"), parse_mode="HTML", reply_markup=issue_status_kb())
    await state.set_state(CreateIssue.status)


@router.message(CreateIssue.priority)
async def priority_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(_("Please select one of the options on the keyboard."), reply_markup=issue_priority_kb())


@router.callback_query(CreateIssue.status, F.data.startswith("iss_status_"), F.data.as_("data"), flags={"set_headers":"set_headers"})
async def status_selected(callback: types.CallbackQuery, data: types.CallbackQuery, state: FSMContext, user_headers):
    data = data.removeprefix("iss_status_")

    if data != "Done":
        status = data[:2] + "" + data[2:]
    else:
        status = data

    await state.update_data(status=status)
    user_data = await state.get_data()

    result = make_issue(user_data, user_headers)

    if result == 201:
        await callback.message.answer(_("The issue has been successfully created!"))
        callback.answer()
    else:
        await callback.message.answer(_("An error occurred, the issue was NOT created! Try again"))
        callback.answer()

    await state.clear()


@router.message(CreateIssue.status)
async def status_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(_("Please select one of the options on the keyboard."), reply_markup=issue_status_kb())
