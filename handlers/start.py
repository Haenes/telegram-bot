from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from aiogram_dialog import DialogManager, StartMode

from dialog.states import StartSG, LoginSG, SettingsSG


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(StartSG.start, mode=StartMode.RESET_STACK)


@router.message(Command("login"))
async def cmd_login(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(LoginSG.email, mode=StartMode.RESET_STACK)


@router.message(Command("settings"))
async def cmd_settings(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(SettingsSG.main, mode=StartMode.RESET_STACK)
