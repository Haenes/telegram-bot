from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def settings_kb() -> InlineKeyboardMarkup:
    """ Creates an inline-keyboard with language and timezone settings buttons in one row """

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=_("Language"),
        callback_data="language"
        )
    )
    builder.add(types.InlineKeyboardButton(
        text=_("Timezone"),
        callback_data="timezone"
        )
    )
    
    return builder.as_markup()


def language_kb() -> InlineKeyboardMarkup:
    """ Creates an inline-keyboard with two buttons in one row. """

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text="English 🇺🇸",
        callback_data="lang_en"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text="Русский 🇷🇺",
        callback_data="lang_ru"
        )
    )

    return builder.as_markup()


def timezone_kb() -> InlineKeyboardMarkup:
    """ Creates an inline-keyboard with three buttons in one row. """

    builder = InlineKeyboardBuilder()
    texts = ["UTC", "Moscow", "Vladivostok"]

    for timezone in texts:
        builder.add(types.InlineKeyboardButton(
            text=_(timezone),
            callback_data=f"time_{timezone}"
        )
    )

    return builder.as_markup()
