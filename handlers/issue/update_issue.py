from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from handlers.bugtracker_api import set_up, get_issue, update_issue
from keyboards.for_issues import make_row_keyboard, make_priority_keyboard


router = Router()

# Will be used for the keyboard
ISSUE_TYPE = ["Bug", "Feature"]
ISSUE_PRIORITY = ["Lowest", "Low", "Medium", "High", "Highest"]
ISSUE_STATUS = ["To do", "In progress", "Done"]


class UpdateIssue(StatesGroup):
    title = State()
    description = State()
    key = State()
    type = State()
    priority = State()
    status = State()


issue_data = {}


@router.callback_query(F.data.startswith("iss_change_"), F.data.as_("data"))
async def change_update(callback: types.CallbackQuery, state: FSMContext, data: types.CallbackQuery):
    # It is necessary to fill in issue data once and take them from it, 
	# instead of calling a "get_issue" function in each handler to get data
    global issue_data
    
    headers = set_up()
    issue_id = data.removeprefix("iss_change_")
    issue_data = get_issue(issue_id, headers)

    text = f"""
Now you will need to enter the data one by one to update issue. 
<u>Note</u>: you can cancel the update process by entering: /cancel. \n
<b>Previous issue title: {issue_data['title']}</b>
<b>Enter new issue title:</b>
            """
    
    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateIssue.title)
    await callback.answer()


@router.message(UpdateIssue.title)
async def title_enter(message: types.Message, state: FSMContext):
    # Set a project without the user's input
    await state.update_data(project=issue_data["project"])
    await state.update_data(title=message.text)

    text = f"""
Good, now enter the issue description. \n
<b>Previous issue description: {issue_data['description']}</b>
<b>Enter new issue description:</b>
            """

    await message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateIssue.description)


@router.message(UpdateIssue.description)
async def description_enter(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    text = f"""
Good, now enter the issue key. \n
<b>Previous issue key: {issue_data['key']}</b>
<b>Enter new issue key:</b>
            """

    await message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateIssue.key)


@router.message(UpdateIssue.key)
async def key_enter(message: types.Message, state: FSMContext):
    await state.update_data(key=message.text)

    text = f"""
Good, now select the issue type. \n
<b>Previous issue type: {issue_data['type']}</b>
<b>Select new issue type:</b>
            """

    await message.answer(text, parse_mode="HTML", reply_markup=make_row_keyboard(ISSUE_TYPE))
    await state.set_state(UpdateIssue.type)


@router.message(UpdateIssue.type, F.text.in_(ISSUE_TYPE))
async def type_selected(message: types.Message, state: FSMContext):
    await state.update_data(type=message.text)

    text = f"""
Good, now select the issue priority \n
<b>Previous issue priority: {issue_data['priority']}</b>
<b>Select new issue priority:</b>
            """

    await message.answer(text, parse_mode="HTML", reply_markup=make_priority_keyboard(ISSUE_PRIORITY))
    await state.set_state(UpdateIssue.priority)


@router.message(UpdateIssue.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(ISSUE_TYPE))


@router.message(UpdateIssue.priority, F.text.in_(ISSUE_PRIORITY))
async def priority_selected(message: types.Message, state: FSMContext):
    await state.update_data(priority=message.text)

    text = f"""
Good, now enter the issue status. \n
<b>Previous issue status: {issue_data['status']}</b>
<b>Select new issue status:</b>
            """

    await message.answer(text, parse_mode="HTML", reply_markup=make_row_keyboard(ISSUE_STATUS))
    await state.set_state(UpdateIssue.status)


@router.message(UpdateIssue.priority)
async def priority_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(ISSUE_PRIORITY))


@router.message(UpdateIssue.status, F.text.in_(ISSUE_STATUS))
async def status_selected(message: types.Message, state: FSMContext):
    await state.update_data(status=message.text)
    user_data = await state.get_data()

    headers = set_up()
    result = update_issue(issue_data["id"], user_data, headers)

    if result == 200:
        await message.answer("The issue has been successfully updated!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("An error occurred, the issue was NOT updated!", reply_markup=ReplyKeyboardRemove())

    await state.clear()


@router.message(UpdateIssue.status)
async def status_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(ISSUE_STATUS))