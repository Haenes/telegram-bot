from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from handlers.bugtracker_api import set_up, convert_project_to_url, make_issue
from keyboards.for_issues import make_row_keyboard, make_priority_keyboard


router = Router()

# Will be used for the keyboard
ISSUE_TYPE = ["Bug", "Feature"]
ISSUE_PRIORITY = ["Lowest", "Low", "Medium", "High", "Highest"]
ISSUE_STATUS = ["To do", "In progress", "Done"]


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

    text = f"""
Now you will need to enter the data one by one to create a new issue. 
<u>Note</u>: you can cancel the creation process by entering: /cancel. \n
<b>Enter related to issue project:</b>
            """

    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(CreateIssue.project)
    await callback.answer()


@router.message(CreateIssue.project)
async def project_enter(message: types.Message, state: FSMContext):
    project = convert_project_to_url(message.text)

    if project == "UnboundLocalError":
        await message.answer("Project not found! Please, try again!")
    else: 
        await state.update_data(project=project)  
        await message.answer("Good, now <b>enter the issue title:</b>", parse_mode="HTML")
        await state.set_state(CreateIssue.title)


@router.message(CreateIssue.project)
async def project_enter_incorrect(message: types.Message, state: FSMContext):
    await message.answer("Invalid project name, please, try again!")


@router.message(CreateIssue.title)
async def title_enter(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Good, now <b>enter the issue description:</b>", parse_mode="HTML")
    await state.set_state(CreateIssue.description)


@router.message(CreateIssue.description)
async def description_enter(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Good, now <b>enter the issue key:</b>", parse_mode="HTML")
    await state.set_state(CreateIssue.key)


@router.message(CreateIssue.key)
async def key_enter(message: types.Message, state: FSMContext):
    await state.update_data(key=message.text)
    await message.answer("Good, now <b>select the issue type:</b>", parse_mode="HTML", reply_markup=make_row_keyboard(ISSUE_TYPE))
    await state.set_state(CreateIssue.type)


@router.message(CreateIssue.type, F.text.in_(ISSUE_TYPE))
async def type_selected(message: types.Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer("Good, now <b>select the issue priority:</b>", parse_mode="HTML", reply_markup=make_priority_keyboard(ISSUE_PRIORITY))
    await state.set_state(CreateIssue.priority)


@router.message(CreateIssue.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(ISSUE_TYPE))


@router.message(CreateIssue.priority, F.text.in_(ISSUE_PRIORITY))
async def priority_selected(message: types.Message, state: FSMContext):
    await state.update_data(priority=message.text)
    await message.answer("Good, now <b>select the issue status:</b>", parse_mode="HTML", reply_markup=make_row_keyboard(ISSUE_STATUS))
    await state.set_state(CreateIssue.status)


@router.message(CreateIssue.priority)
async def priority_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_priority_keyboard(ISSUE_PRIORITY))


@router.message(CreateIssue.status, F.text.in_(ISSUE_STATUS))
async def status_selected(message: types.Message, state: FSMContext):
    await state.update_data(status=message.text)
    user_data = await state.get_data()
    
    headers = set_up()
    result = make_issue(user_data, headers)

    if result == 201:
        await message.answer("The issue has been successfully created!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("An error occurred, the issue was NOT created! Try again", reply_markup=ReplyKeyboardRemove())

    await state.clear()


@router.message(CreateIssue.status)
async def status_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(ISSUE_STATUS))
