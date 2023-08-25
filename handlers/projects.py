from aiogram import Router, types, F

from handlers.bugtracker_api import set_up, get_projects, get_project, delete_project
from keyboards.for_projects import projects_kb, project_kb


router = Router()


@router.callback_query(F.data == "projects")
async def send_projects(callback: types.CallbackQuery):
    headers = set_up()
    results = get_projects(headers)
    
    await callback.message.answer("List of projects:", reply_markup=projects_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("project_"), F.data.as_("data"))
async def send_project(callback: types.CallbackQuery, data: types.CallbackQuery):
    headers = set_up()
    project_id = data.removeprefix("project_")
    results = get_project(project_id, headers)

    await callback.message.answer(f"Name: {results['name']} \nDescription: {results['description']} \nKey: {results['key']} \nType: {results['type']} \nFavorite: {results['starred']} \nCreated: {results['created']}", reply_markup=project_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("prj_delete_"), F.data.as_("data"))
async def del_project(callback: types.CallbackQuery, data):
    headers = set_up()
    project_id = data.removeprefix("prj_delete_")
    results = delete_project(project_id, headers)

    await callback.message.answer(results)
    await callback.answer()
