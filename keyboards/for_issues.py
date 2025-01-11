from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def issues_kb(results: dict | str) -> InlineKeyboardMarkup:
    """ Make every issue - inline button.

    Plus add navigation buttons and button to create a new one.
    """
    builder = InlineKeyboardBuilder()

    if isinstance(results, str):
        builder.row(InlineKeyboardButton(
            text=_("Create"),
            callback_data=f"create_issue_{results}"
        ))
        return builder.as_markup()

    issues = [issue for issue in results["results"]]

    for issue in issues:
        builder.add(InlineKeyboardButton(
            text=issue["title"],
            callback_data=f"issue_{issue['project_id']}_{issue['id']}"
        ))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(
        text=_("Create"),
        callback_data=f"create_issue_{issues[0]['project_id']}"
    ))
    pagination_kb(results, builder)

    return builder.as_markup()


def issue_kb(results: dict) -> InlineKeyboardMarkup:
    """ Creates a keyboard with "Change" and "Delete" buttons in one row. """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text=_("Change"),
        callback_data=f"change_issue_{results['project_id']}_{results['id']}"
    ))
    builder.add(InlineKeyboardButton(
        text=_("Delete"),
        callback_data=f"delete_issue_{results['project_id']}_{results['id']}"
    ))
    return builder.as_markup()


def issue_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    types = ["Bug", "Feature"]

    for type in types:
        builder.add(InlineKeyboardButton(
            text=_(type),
            callback_data=f"iss_type_{type}"
        ))
    return builder.as_markup()


def issue_priority_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = ["Lowest", "Low", "Medium", "High", "Highest"]

    for priority in texts:
        builder.add(InlineKeyboardButton(
            text=_(priority),
            callback_data=f"iss_priority_{priority}"
        ))
    builder.adjust(3)
    return builder.as_markup()


def issue_status_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    statuses = ["To do", "In progress", "Done"]

    for status in statuses:
        builder.add(InlineKeyboardButton(
            text=_(status),
            callback_data=f"iss_status_{status}"
        ))
    return builder.as_markup()


def pagination_kb(results: dict, builder: InlineKeyboardBuilder):
    project_id = results["results"][0]["project_id"]
    next_page = f"next_issues_{project_id}_{results['next_page']}"
    prev_page = f"prev_issues_{project_id}_{results['prev_page']}"
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
