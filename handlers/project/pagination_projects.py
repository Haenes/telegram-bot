from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from aiohttp import ClientSession

from handlers.bugtracker_api import Project
from keyboards.for_projects import projects_kb


router = Router()


@router.callback_query(
    F.data.startswith("next_projects_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def next_projects(
    callback: CallbackQuery,
    data: str,
    user_headers: dict,
    session: ClientSession
):
    page = data.removeprefix("next_projects_")
    results = await Project().pagination_next(session, user_headers, page)

    await callback.message.answer(
        _("List of projects, page {page}:").format(page=page),
        reply_markup=projects_kb(results)
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("back_projects_"),
    F.data.as_("data"),
    flags={"set_headers": "set_headers"}
)
async def back_projects(
    callback: CallbackQuery,
    data: str,
    user_headers: dict,
    session: ClientSession
):
    page = data.removeprefix("back_projects_")
    results = await Project().pagination_back(session, user_headers, page)

    await callback.message.answer(
        _("List of projects, page {page}:").format(page=page),
        reply_markup=projects_kb(results)
    )
    await callback.answer()
