from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from handlers.bugtracker_api import get_translated_timezone


def settings_kb() -> InlineKeyboardMarkup:
    """ Creates a keyboard with language and timezone settings buttons. """
    builder = InlineKeyboardBuilder()
    settings = ["language", "timezone"]

    for setting in settings:
        builder.add(types.InlineKeyboardButton(
            text=_(setting.capitalize()),
            callback_data=setting
        ))
    return builder.as_markup()


def language_kb() -> InlineKeyboardMarkup:
    """ Creates a keyboard with language buttons in one row. """
    builder = InlineKeyboardBuilder()
    languages = {"en": "English 🇺🇸", "ru": "Русский 🇷🇺"}

    for code, text in languages.items():
        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data=f"lang_{code}"
        ))
    return builder.as_markup()


def timezone_kb() -> InlineKeyboardMarkup:
    """ Creates a keyboard with three timezone buttons in one row. """
    builder = InlineKeyboardBuilder()
    timezones = ["UTC", "Moscow", "Vladivostok"]

    for timezone in timezones:
        builder.add(types.InlineKeyboardButton(
            text=get_translated_timezone(timezone),
            callback_data=f"time_{timezone}"
        ))
    return builder.as_markup()
