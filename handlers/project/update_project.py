from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from handlers.bugtracker_api import set_up, get_project, update_project
from keyboards.for_projects import make_row_keyboard


router = Router()

# Will be used for the keyboard
PROJECT_TYPES = ["Fullstack", "Front-end", "Back-end"]
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

    text = _("""
Now you will need to enter the data one by one to update project. 
<u>Note</u>: you can cancel the update process by entering: /cancel. \n
<b>Previous name: {name}</b>
<b>New name:</b>
            """).format(name=project_data['name'])
    
    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateProject.name)
    await callback.answer()


@router.message(UpdateProject.name)
async def name_enter(message: Message, state: FSMContext):
    await state.update_data(name=message.text.title())

    text = _("""
Good, now enter description of the project. \n
<b>Previous description: {description}</b>
<b>New description:</b>
            """).format(description=project_data['description'])

    await message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateProject.description)


@router.message(UpdateProject.description)
async def description_enter(message: Message, state: FSMContext):
    await state.update_data(description=message.text.title())

    text = _("""
Good, now enter key of the project. \n
<b>Previous key: {key}</b>
<b>New key:</b>
            """).format(key=project_data['key'])

    await message.answer(text, parse_mode="HTML")
    await state.set_state(UpdateProject.key)


@router.message(UpdateProject.key)
async def key_enter(message: Message, state: FSMContext):
    await state.update_data(key=message.text)

    text = _("""
Good, now choose type of the project. \n
<b>Previous type: {type}</b>
<b>New type:</b>
            """).format(type=project_data['type'])

    await message.answer(text, parse_mode="HTML", reply_markup=make_row_keyboard(PROJECT_TYPES))
    await state.set_state(UpdateProject.type)


@router.message(UpdateProject.type, F.text.in_(PROJECT_TYPES))
async def type_selected(message: Message, state: FSMContext):
    await state.update_data(type=message.text)

    text = _("""
Good, now choose whether the project will be a favorite or not. \n
<b>Earlier: {starred}</b>
<b>Now:</b>
            """).format(starred=project_data['starred'])

    await message.answer(text, parse_mode="HTML", reply_markup=make_row_keyboard(PROJECT_FAVORITE))
    await state.set_state(UpdateProject.starred)


@router.message(UpdateProject.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(_("Please select one of the options on the keyboard."), reply_markup=make_row_keyboard(PROJECT_TYPES))


@router.message(UpdateProject.starred, F.text.in_(PROJECT_FAVORITE))
async def favorite_selected(message: Message, state: FSMContext):
    await state.update_data(starred=message.text)
    user_data = await state.get_data()

    headers = set_up()
    results = update_project(project_data["id"], user_data, headers)

    if results == 200:
        await message.answer(text=_("The project has been successfully updated!"), reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text=_("An error occurred, the project was NOT updated!"), reply_markup=ReplyKeyboardRemove())
    
    await state.clear()


@router.message(UpdateProject.starred)
async def favorite_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(text=_("Please select one of the options on the keyboard."), reply_markup=make_row_keyboard(PROJECT_FAVORITE))
