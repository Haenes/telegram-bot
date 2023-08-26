from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def projects_kb(results) -> InlineKeyboardMarkup:
    projects = [project for project in results["results"]]

    builder = InlineKeyboardBuilder()

    for project in projects:
        builder.add(types.InlineKeyboardButton(
            text=project["name"],
            callback_data=f"project_{project['id']}"
            )
        )
    builder.adjust(2)
    
    builder.row(types.InlineKeyboardButton(
        text="Create new",
        callback_data="create_project"
        )
    )

    if results["previous"] != None:
        builder.row(types.InlineKeyboardButton(
            text="<< Back",
            callback_data="back_projects"
            )
        )

    if results["next"] != None:
        builder.row(types.InlineKeyboardButton(
            text="Next >>",
            callback_data="next_projects"
            )
        )

    return builder.as_markup()


def project_kb(results):
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text="Change",
        callback_data=f"prj_change_{results['id']}"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text="Delete",
        callback_data=f"prj_delete_{results['id']}"
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
