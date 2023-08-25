from aiogram import types
from aiogram.types import InlineKeyboardMarkup
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
