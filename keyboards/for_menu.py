from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def menu_kb() -> InlineKeyboardMarkup:
    """ Creates an inline-keyboard with Projects and Issues buttons
    in one row
    """

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=_("Projects"),
        callback_data="projects"
        )
    )
    builder.add(types.InlineKeyboardButton(
        text=_("Issues"),
        callback_data="issues"
        )
    )

    return builder.as_markup()
