from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """ Cancels the process of creating a Project/Issue. """
    await clear_state_and_save_data(state)
    await message.answer(
        text=_("Action canceled."),
        reply_markup=ReplyKeyboardRemove()
    )


async def clear_state_and_save_data(state: FSMContext) -> None:
    """ Clear the state and save the language and timezone (if any).

    Due to the fact that state.clear() clears all data
    without exception, this function takes out
    the language and time zone (data that does not need to be deleted)
    and sets them after cleaning. This way, the user will not need
    to change the language and time zone to the desired one
    every time after creating/changing a project/issue.
    """

    data = await state.get_data()
    locale_and_timezone = {}
    locale_and_timezone["locale"] = data["locale"]

    if "timezone" in data:
        locale_and_timezone["timezone"] = data["timezone"]

    await state.clear()
    await state.set_data(locale_and_timezone)
