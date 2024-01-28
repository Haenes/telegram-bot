from aiogram import types
from aiogram.types import InlineKeyboardMarkup
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


def issue_type_kb() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text=_("Bug"),
        callback_data="iss_type_Bug"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text=_("Feature"),
        callback_data="iss_type_Feature"
        )
    )

    return builder.as_markup()


def issue_priority_kb() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    texts = ["Lowest", "Low", "Medium", "High", "Highest"]

    for priority in texts:
        builder.add(types.InlineKeyboardButton(
            text=_(priority),
            callback_data=f"iss_priority_{priority}"
            )
        )

    builder.adjust(3)
    return builder.as_markup()


def issue_status_kb() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    texts = ["To do", "In progress", "Done"]

    for status in texts:
        builder.add(types.InlineKeyboardButton(
            text=_(status),
            callback_data=f"iss_status_{status}"
            )
        )

    return builder.as_markup()
