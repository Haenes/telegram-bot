from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from aiohttp import ClientSession

from handlers.bugtracker_api import Project
from handlers.common import clear_state_and_save_data
from keyboards.for_projects import project_favorite_kb


router = Router()
project_data = {}


class UpdateProject(StatesGroup):
    name = State()
    key = State()
    starred = State()


@router.callback_query(
    F.data.startswith("prj_change_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def change_project(
    callback: CallbackQuery,
    state: FSMContext,
    data: str,
    user_headers: dict,
    session: ClientSession
):
    # It is necessary to fill in project data once and take them from it,
    # instead of calling a "get_project" function in each handler to get data
    global project_data

    project_id = data.removeprefix("prj_change_")
    project_data = await Project.get_item(session, project_id, user_headers)
    project_data["id"] = project_id

    text = _(
        """
            Now you will need to enter the data one by one to update project.\
            \n<u>Note</u>: you can cancel the update process by command:  /cancel.
            \n<b>Previous name: {name}</b>\
            \n<b>New name:</b>
        """
    ).format(name=project_data['name'])

    await callback.message.answer(text)
    await state.set_state(UpdateProject.name)
    await callback.answer()


@router.message(UpdateProject.name)
async def name_enter(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    text = _(
        """
            Good, now enter key of the project.
            \n<b>Previous key: {key}</b>\
            \n<b>New key:</b>
        """
    ).format(key=project_data['key'])

    await message.answer(text)
    await state.set_state(UpdateProject.key)


@router.message(UpdateProject.key)
async def key_enter(message: Message, state: FSMContext):
    await state.update_data(key=message.text)
    text = _(
        """
            Good, now choose whether the project will be a favorite or not.
            \n<b>Earlier: {starred}</b>\
            \n<b>Now:</b>
        """
    ).format(starred=Project.get_translated_starred(project_data["starred"]))

    await message.answer(text, reply_markup=project_favorite_kb())
    await state.set_state(UpdateProject.starred)


@router.callback_query(
    UpdateProject.starred,
    F.data.startswith("prj_favorite_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def favorite_selected(
    callback: CallbackQuery,
    data: str,
    state: FSMContext,
    user_headers,
    session: ClientSession
):
    await state.update_data(starred=data.removeprefix("prj_favorite_"))
    user_data = await state.get_data()
    results = await Project().edit_item(
        session,
        project_data["id"],
        user_headers,
        user_data
    )

    await callback.message.answer(results)
    await callback.answer()
    await clear_state_and_save_data(state)


@router.message(UpdateProject.starred)
async def favorite_selected_incorrect(message: Message, state: FSMContext):
    await message.answer(
        text=_("Please select one of the options on the keyboard."),
        reply_markup=project_favorite_kb()
    )
