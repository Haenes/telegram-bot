from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def issues_kb(results) -> InlineKeyboardMarkup:
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
        text="Create new",
        callback_data="create_issue"
        )
    )

    if results["previous"] != None:
        builder.row(types.InlineKeyboardButton(
            text="<< Back",
            callback_data="back_issues"
            )
        )

    if results["next"] != None:
        builder.row(types.InlineKeyboardButton(
            text="Next >>",
            callback_data="next_issues"
            )
        )

    return builder.as_markup()


def issue_kb(results):
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text="Change",
        callback_data=f"iss_change_{results['id']}"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text="Delete",
        callback_data=f"iss_delete_{results['id']}"
        )
    )

    return builder.as_markup()


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Creates a replay keyboard with buttons in one row
    items: list of texts for buttons
    """

    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_priority_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Creates a replay keyboard with buttons in two rows
    items: list of texts for buttons
    """

    row1 = [KeyboardButton(text=item) for item in items[:2]]
    row2 = [KeyboardButton(text=item) for item in items[2:]]
    return ReplyKeyboardMarkup(keyboard=[row1, row2], resize_keyboard=True)
