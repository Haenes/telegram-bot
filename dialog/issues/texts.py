from aiogram.utils.i18n import gettext as _


async def issues(*args, **kwargs):
    return {
        "issues_text": _("Your issues:"),
        "zero_issues": _("You don't have issues yet."),
        "back": _("Back"),
        "cancel": _("Cancel"),
        "create": _("Create new"),
        "title_text": _("Enter issue title:"),
        "description_text": _("Enter description of issue:"),
        "type_text": _("Is this project will be a favorite:"),
        "priority_text": _("Is this project will be a favorite:"),
    }


async def create(*args, **kwargs):
    return {
        "cancel": _("Cancel"),
        "skip": _("Skip"),
        "title_text": _("Enter issue title:"),
        "description_text": _("Enter description of issue:"),
        "type_text": _("Select the issue type:"),
        "types": [(_("Feature"), "Feature"), (_("Bug"), "Bug")],
        "priority_text": _(
            "Select the priority of the issue. "
            "\nDefault is <b>Medium</b>:"
        ),
        "prioritys": [
            (_("Lowest"), "Lowest"),
            (_("Low"), "Low"),
            (_("Medium"), "Medium"),
            (_("High"), "High"),
            (_("Highest"), "Highest"),
        ],
        "status_text": _("Select the issue status. \nDefault is <b>To do</b>:"),
        "statuses": [
            (_("To do"), "To do"),
            (_("In progress"), "In progress"),
            (_("Done"), "Done"),
        ],
    }


async def issue(*args, **kwargs):
    return {
        "issues": _("Issues"),
        "edit": _("Edit"),
        "delete": _("Delete"),
        "back": _("Back")
    }


async def edit(*args, **kwargs):
    return {
        "instructions": _("Select what you want to change:"),
        "continue": _("Continue"),
        "cancel": _("Cancel"),
        "skip": _("Skip"),
        "title_text": _("Enter issue title:"),
        "description_text": _("Enter description of issue:"),
        "fields": [
            (_("Title"), "1"),
            (_("Description"), "2"),
            (_("Type"), "3"),
            (_("Priority"), "4"),
            (_("Status"), "5"),
        ],
        "type_text": _("Select the issue type:"),
        "types": [(_("Feature"), "Feature"), (_("Bug"), "Bug")],
        "priority_text": _("Select the priority of the issue."),
        "prioritys": [
            (_("Lowest"), "Lowest"),
            (_("Low"), "Low"),
            (_("Medium"), "Medium"),
            (_("High"), "High"),
            (_("Highest"), "Highest"),
        ],
        "status_text": _("Select the issue status."),
        "statuses": [
            (_("To do"), "To do"),
            (_("In progress"), "In progress"),
            (_("Done"), "Done"),
        ],
    }
