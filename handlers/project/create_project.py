from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import set_up, make_project
from keyboards.for_projects import make_row_keyboard, project_favorite_kb


router = Router()

# Will be used for the keyboard
PROJECT_TYPES = ["Fullstack", "Front-end", "Back-end"]

class CreateProject(StatesGroup):
    name = State()
    description = State()
    key = State()
    type = State()
    starred = State()


@router.callback_query(F.data == "create_project")
async def create_project(callback: types.CallbackQuery, state: FSMContext):

    text = _("""
Now you will need to enter the data one by one to create a new project. 
<u>Note</u>: you can cancel the creation process by entering: /cancel. \n
<b>Enter project name:</b>
            """)

    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(CreateProject.name)
    await callback.answer()


@router.message(CreateProject.name)
async def name_enter(message: Message, state: FSMContext):
    await state.update_data(name=message.text.title())
    await message.answer(_("Good, now <b>enter description of the project:</b>"), parse_mode="HTML")
    await state.set_state(CreateProject.description)


@router.message(CreateProject.description)
async def description_enter(message: Message, state: FSMContext):
    await state.update_data(description=message.text.title())
    await message.answer(_("Good, now <b>enter key of the project:</b>"), parse_mode="HTML")
    await state.set_state(CreateProject.key)


@router.message(CreateProject.key)
async def key_enter(message: Message, state: FSMContext):
    await state.update_data(key=message.text.upper())
    await message.answer(_("Good, now <b>select type of the project:</b>"), parse_mode="HTML", reply_markup=make_row_keyboard(PROJECT_TYPES))
    await state.set_state(CreateProject.type)

  
@router.message(CreateProject.type, F.text.in_(PROJECT_TYPES))
async def type_selected(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer(_("Good, now <b>select whether the project will be a favorite or not:</b>"), parse_mode="HTML", reply_markup=project_favorite_kb())
    await state.set_state(CreateProject.starred)


@router.message(CreateProject.type)
async def type_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(_("Please select one of the options on the keyboard."), reply_markup=make_row_keyboard(PROJECT_TYPES))

@router.callback_query(CreateProject.starred, F.data.startswith("prj_favorite_"), F.data.as_("data"))
async def favorite_selected(callback: types.CallbackQuery, data: types.CallbackQuery, state: FSMContext):
    favorite = data.removeprefix("prj_favorite_")

    await state.update_data(starred=favorite)
    user_data = await state.get_data()

    headers = set_up()
    results = make_project(user_data, headers)

    if results == 201:
        await callback.message.answer(_("The project has been successfully created!"))
        await callback.answer()
    else:
        await callback.message.answer(_("An error occurred, the project was NOT created!"))
        await callback.answer()
    
    await state.clear()


@router.message(CreateProject.starred)
async def favorite_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(_("Please select one of the options on the keyboard."), reply_markup=project_favorite_kb())
