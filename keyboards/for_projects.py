from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def projects_kb(results: dict | str) -> InlineKeyboardMarkup:
    """ Make every project - inline button.

    Plus add navigation buttons and button to create a new one.
    """
    builder = InlineKeyboardBuilder()

    if isinstance(results, str):
        builder.row(InlineKeyboardButton(
            text=_("Create"),
            callback_data="create_project"
        ))
        return builder.as_markup()

    projects = [project for project in results["results"]]

    for project in projects:
        builder.add(InlineKeyboardButton(
            text=project["name"],
            callback_data=f"project_{project['id']}"
        ))

    builder.adjust(2)
    builder.row(InlineKeyboardButton(
        text=_("Create"),
        callback_data="create_project"
    ))
    pagination_kb(results, builder)

    return builder.as_markup()


def project_kb(results: dict) -> InlineKeyboardMarkup:
    """
    Creates a keyboard with "Issues", "Change", "Delete" buttons in one row.
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=_("Issues"),
            callback_data=f"issues_{results['id']}"
        ),
        InlineKeyboardButton(
            text=_("Change"),
            callback_data=f"prj_change_{results['id']}"
        ),
        InlineKeyboardButton(
            text=_("Delete"),
            callback_data=f"prj_delete_{results['id']}"
        )
    )
    return builder.as_markup()


def project_favorite_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = ["True", "False"]

    for text in texts:
        builder.add(
            InlineKeyboardButton(
                text=_(text),
                callback_data=f"prj_favorite_{text}"
            )
        )

    return builder.as_markup()


def pagination_kb(results: dict, builder: InlineKeyboardBuilder):
    next_page = f"next_projects_{results["next_page"]}"
    prev_page = f"back_projects_{results["prev_page"]}"
    buttons = []

    if results["prev_page"]:
        buttons.append(InlineKeyboardButton(
            text=_("<< Back"),
            callback_data=prev_page
        ))
    if results["next_page"]:
        buttons.append(InlineKeyboardButton(
            text=_("Next >>"),
            callback_data=next_page
        ))

    return builder.row(*buttons)
