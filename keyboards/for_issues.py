from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def issues_kb(results) -> InlineKeyboardMarkup:
    """ 
    Make every issue - inline button.
    Plus add navigation buttons and button to create a new one
    """
        
    issues = [issue for issue in results["results"]]

    builder = InlineKeyboardBuilder()

    for issue in issues:
        builder.add(types.InlineKeyboardButton(
            text=issue['title'],
            callback_data=f"issue_{issue['id']}"
            )
        )
    builder.adjust(2)

    builder.row(types.InlineKeyboardButton(
        text=_("Create"),
        callback_data="create_issue"
        )
    )

    if results["previous"] != None:

        if results["previous"] == "http://127.0.0.1:8000/api/issues/":
            page = 1
        else:
            page = results["previous"].removeprefix("http://127.0.0.1:8000/api/issues/?page=")

        builder.row(types.InlineKeyboardButton(
            text=_("<< Back"),
            callback_data=f"back_issues_{page}"
            )
        )

    if results["next"] != None:
        page = results["next"].removeprefix("http://127.0.0.1:8000/api/issues/?page=")

        builder.row(types.InlineKeyboardButton(
            text=_("Next >>"),
            callback_data=f"next_issues_{page}"
            )
        )

    return builder.as_markup()


def issue_kb(results) -> InlineKeyboardMarkup:
    """ Creates an inline-keyboard with two button in one row. """

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text=_("Change"),
        callback_data=f"iss_change_{results['id']}"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text=_("Delete"),
        callback_data=f"iss_delete_{results['id']}"
        )
    )

    return builder.as_markup()


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Creates a replay keyboard with buttons in one row.
    items: list of texts for buttons
    """

    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_priority_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Creates a special version of the make_row_keyboard(), 
    because on the phone the priorities in one row look ugly.
    """

    row1 = [KeyboardButton(text=item) for item in items[:2]]
    row2 = [KeyboardButton(text=item) for item in items[2:]]
    return ReplyKeyboardMarkup(keyboard=[row1, row2], resize_keyboard=True)
