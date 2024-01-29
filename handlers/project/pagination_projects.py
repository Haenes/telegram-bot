from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import Paginator
from keyboards.for_projects import projects_kb


router = Router()


@router.callback_query(F.data.startswith("next_projects_"), F.data.as_("data"), flags={"set_headers":"set_headers"})
async def next_projects(callback: types.CallbackQuery, data: types.CallbackQuery, user_headers):
    page = data.removeprefix("next_projects_")
    
    paginator = Paginator(user_headers, page)
    results = paginator.next_projects()
    
    await callback.message.answer(_("List of projects, page {page}:").format(page=page), reply_markup=projects_kb(results))
    await callback.answer()


@router.callback_query(F.data.startswith("back_projects_"), F.data.as_("data"), flags={"set_headers":"set_headers"})
async def back_projects(callback: types.CallbackQuery, data: types.CallbackQuery, user_headers):
    page = data.removeprefix("back_projects_")

    paginator = Paginator(user_headers, page)
    results = paginator.previous_projects()
    
    await callback.message.answer(_("List of projects, page {page}:").format(page=page), reply_markup=projects_kb(results))
    await callback.answer()
