from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """ Cancels the process of creating a Project/Issue """
    await state.clear()
    await message.answer(
        text=_("Action canceled."),
        reply_markup=ReplyKeyboardRemove
        )
