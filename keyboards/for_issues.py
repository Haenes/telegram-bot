from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def issues_kb(results) -> InlineKeyboardMarkup:
    issues = [issue for issue in results["results"]]

    builder = InlineKeyboardBuilder()

    for issue in issues:
        builder.add(types.InlineKeyboardButton(
            text=issue["title"],
            callback_data=f"issue_{issue['id']}"
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
    builder.adjust(2)

    return builder.as_markup()
