import os

from aiogram import Router, types, F

from handlers.bugtracker_api import get_projects, get_project
from keyboards.for_projects import projects_kb


router = Router()


@router.callback_query(F.data == "projects")
async def send_projects(callback: types.CallbackQuery):
    token = os.environ.get('API_TOKEN')
    HEADERS = {"Authorization": f"Token {token}"}

    results = get_projects(HEADERS)
    print(results)
    
    await callback.message.answer("List of projects:", reply_markup=projects_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("project_"))
async def send_project(callback: types.CallbackQuery):
    token = os.environ.get("API_TOKEN")
    HEADERS = {"Authorization": f"Token {token}"}

    results = get_project(63, HEADERS)
    print(results)

    await callback.message.answer(f"Name: {results['name']} \nKey: {results['key']} \nType: {results['type']} \nFavorite: {results['starred']} \nCreated: {results['created']}")
    await callback.answer()
