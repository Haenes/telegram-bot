from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu_kb() -> InlineKeyboardMarkup:
    """ Creates an inline-keyboard with Projects and Issues buttons in one row """

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Projects",
        callback_data="projects"
        )
    )
    builder.add(types.InlineKeyboardButton(
        text="Issues",
        callback_data="issues"
        )
    )
    
    return builder.as_markup()
