from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove


router = Router()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """ Cancels the process of creating a Project/Issue """
    await state.clear()
    await message.answer(text="Action canceled.", reply_markup=ReplyKeyboardRemove)
