from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.utils.i18n import gettext as _

from aiogram_dialog import DialogManager, StartMode

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from dialog.basic.states import StartSG, LoginSG, MenuSG
from dialog.utils import get_token


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(StartSG.main, mode=StartMode.RESET_STACK)


@router.message(Command("login"))
async def cmd_login(
    message: Message,
    redis: Redis,
    sessionmaker: async_sessionmaker,
    dialog_manager: DialogManager
):
    if await get_token(sessionmaker, redis, message.from_user.id):
        return await message.answer(_("You're already logged in."))
    await dialog_manager.start(LoginSG.email, mode=StartMode.RESET_STACK)


@router.message(Command("menu"))
async def cmd_menu(
    message: Message,
    redis: Redis,
    sessionmaker: async_sessionmaker,
    dialog_manager: DialogManager
):
    if not await get_token(sessionmaker, redis, message.from_user.id):
        return await message.answer(_(
            "You're not logged in. Use /login command."
        ))
    await dialog_manager.start(MenuSG.main, mode=StartMode.RESET_STACK)
