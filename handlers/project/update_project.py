from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from handlers.bugtracker_api import set_up, get_project, update_project
from keyboards.for_projects import make_row_keyboard


router = Router()

# Will be used for the keyboard
PROJECT_TYPES = ["Fullstack software", "Front-end software", "Back-end software"]
PROJECT_FAVORITE = [str(True), str(False)]


class UpdateProject(StatesGroup):
    name = State()
    description = State()
    key = State()
    type = State()
    starred = State()


project_data = {}


@router.callback_query(F.data.startswith("prj_change_"), F.data.as_("data"))
async def change_project(callback: types.CallbackQuery, state: FSMContext, data: types.CallbackQuery):
    # It is necessary to fill in project data once and take them from it, 
	# instead of calling a "get_project" function in each handler to get data
    global project_data
    
    headers = set_up()
    project_id = data.removeprefix("prj_change_")
    project_data = get_project(project_id, headers)
    
    await callback.message.answer(f"Now you will need to enter the data one by one to update project. \n\nNote: you can cancel the update process by entering the command: /cancel. \n\nPrevious project name: {project_data['name']} \nEnter new project name:")
    await state.set_state(UpdateProject.name)
    await callback.answer()


@router.message(UpdateProject.name)
async def name_enter(message: Message, state: FSMContext):
    await state.update_data(name=message.text.title())
    await message.answer(f"Good, now enter description of the project. \n\nPrevious description: {project_data['description']} \nEnter new description:")
    await state.set_state(UpdateProject.description)


@router.message(UpdateProject.description)
async def description_enter(message: Message, state: FSMContext):
    await state.update_data(description=message.text.title())
    await message.answer(f"Good, now enter key of the project. \n\nPrevious key: {project_data['key']} \nEnter new key:")
    await state.set_state(UpdateProject.key)


@router.message(UpdateProject.key)
async def key_enter(message: Message, state: FSMContext):
    await state.update_data(key=message.text)
    await message.answer(f"Good, now choose type of the project. \n\nPrevious type: {project_data['type']} \nSelect a new type:", reply_markup=make_row_keyboard(PROJECT_TYPES))
    await state.set_state(UpdateProject.type)


@router.message(UpdateProject.type, F.text.in_(PROJECT_TYPES))
async def type_selected(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer(f"Good, now choose whether the project will be a favorite or not. \n\nEarlier: {project_data['starred']} \nSelect new:", reply_markup=make_row_keyboard(PROJECT_FAVORITE))
    await state.set_state(UpdateProject.starred)


@router.message(UpdateProject.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer("Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(PROJECT_TYPES))


@router.message(UpdateProject.starred, F.text.in_(PROJECT_FAVORITE))
async def favorite_selected(message: Message, state: FSMContext):
    await state.update_data(starred=message.text)
    user_data = await state.get_data()

    headers = set_up()
    results = update_project(project_data["id"], user_data, headers)

    if results == 200:
        await message.answer(text="The project has been successfully updated!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text="An error occurred, the project was NOT updated!", reply_markup=ReplyKeyboardRemove())
    
    await state.clear()


@router.message(UpdateProject.starred)
async def favorite_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(text="Please select one of the options on the keyboard.", reply_markup=make_row_keyboard(PROJECT_FAVORITE))
