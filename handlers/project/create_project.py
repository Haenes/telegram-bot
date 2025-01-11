from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import make_project
from handlers.common import clear_state_and_save_data
from keyboards.for_projects import project_favorite_kb


router = Router()


class CreateProject(StatesGroup):
    name = State()
    key = State()
    starred = State()


@router.callback_query(F.data == "create_project")
async def create_project(callback: CallbackQuery, state: FSMContext):
    text = _(
        """
            Now you will need to enter the data one by one to create a new project.\
            \n<u>Note</u>: you can cancel the creation process by command:  /cancel.
            \n<b>Enter project name:</b>
        """
    )

    await callback.message.answer(text)
    await state.set_state(CreateProject.name)
    await callback.answer()


@router.message(CreateProject.name)
async def name_enter(message: Message, state: FSMContext):
    await state.update_data(name=message.text.title())
    await message.answer(_("Good, now <b>enter key of the project:</b>"))
    await state.set_state(CreateProject.key)


@router.message(CreateProject.key)
async def key_enter(message: Message, state: FSMContext):
    await state.update_data(key=message.text.upper())
    await message.answer(
        _(
            "Good, now <b>select whether the project "
            "will be a favorite or not:</b>"
        ),
        reply_markup=project_favorite_kb()
    )
    await state.set_state(CreateProject.starred)


@router.callback_query(
    CreateProject.starred,
    F.data.startswith("prj_favorite_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def favorite_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext,
    user_headers: dict
):
    favorite = data.removeprefix("prj_favorite_")
    await state.update_data(starred=favorite)
    user_data = await state.get_data()

    results = await make_project(user_headers, user_data)

    await callback.message.answer(results)
    await callback.answer()
    await clear_state_and_save_data(state)


@router.message(CreateProject.starred)
async def favorite_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        _("Please select one of the options on the keyboard."),
        reply_markup=project_favorite_kb()
    )
