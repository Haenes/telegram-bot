from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def projects_kb(results) -> InlineKeyboardMarkup:
    """ 
    Make every project - inline button.
    Plus add navigation buttons and button to create a new one.
    """

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
        text=_("Create"),
        callback_data="create_project"
        )
    )

    if results["previous"] != None:

        if results["previous"] == "http://127.0.0.1:8000/api/projects/":
            page = 1
        else:
            page = results["previous"].removeprefix("http://127.0.0.1:8000/api/projects/?page=")

        builder.row(types.InlineKeyboardButton(
            text=_("<< Back"),
            callback_data=f"back_projects_{page}"
            )
        )

    if results["next"] != None:
        page = results["next"].removeprefix("http://127.0.0.1:8000/api/projects/?page=")

        builder.row(types.InlineKeyboardButton(
            text=_("Next >>"),
            callback_data=f"next_projects_{page}"
            )
        )

    return builder.as_markup()


def project_kb(results) -> InlineKeyboardMarkup:
    """ 
    Creates an inline-keyboard with two button in one row. 

    Change - for change selected project info.
    Delete - delete selected project.
    """

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text=_("Change"),
        callback_data=f"prj_change_{results['id']}"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text=_("Delete"),
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
