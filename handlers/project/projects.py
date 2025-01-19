from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager, StartMode

from dialog.states import ProjectsSG


router = Router()


@router.message(Command("projects"))
async def cmd_projects(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ProjectsSG.main, mode=StartMode.RESET_STACK)
