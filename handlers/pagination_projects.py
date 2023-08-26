from aiogram import Router, types, F

from handlers.bugtracker_api import set_up, Paginator
from keyboards.for_projects import projects_kb


router = Router()


@router.callback_query(F.data.startswith("next_projects_"), F.data.as_("data"))
async def next_projects(callback: types.CallbackQuery, data: types.CallbackQuery):
    page = data.removeprefix("next_projects_")
    
    headers = set_up()
    paginator = Paginator(headers, page)
    results = paginator.next_projects()
    
    await callback.message.answer(f"List of projects, page {page}:", reply_markup=projects_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("back_projects_"), F.data.as_("data"))
async def back_projects(callback: types.CallbackQuery, data: types.CallbackQuery):
    page = data.removeprefix("back_projects_")
    
    headers = set_up()
    paginator = Paginator(headers, page)
    results = paginator.previous_projects()
    
    await callback.message.answer(f"List of projects, page {page}:", reply_markup=projects_kb(results))
    await callback.answer()
