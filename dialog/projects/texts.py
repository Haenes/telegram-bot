from aiogram.utils.i18n import gettext as _


async def projects(*args, **kwargs):
    return {
        "projects_text": _("Your projects:"),
        "zero_projects": _("You don't have projects yet."),
        "back": _("Back"),
        "cancel": _("Cancel"),
        "create": _("Create new"),
        "name_text": _("Enter project name:"),
        "key_text": _("Enter key of the project:"),
        "starred_text": _("Is this project will be a favorite:"),
        "true": _("True"),
        "false": _("False"),
    }


async def create(*args, **kwargs):
    return {
        "cancel": _("Cancel"),
        "name_text": _("Enter project name:"),
        "key_text": _("Enter key of the project:"),
        "starred_text": _("Is this project will be a favorite:"),
        "favorites": [(_("True"), True), (_("False"), False)]
    }


async def project(*args, **kwargs):
    return {
        "issues": _("Issues"),
        "edit": _("Edit"),
        "delete": _("Delete"),
        "back": _("Back")
    }


async def edit(*args, **kwargs):
    return {
        "instructions": _("Select what you want to change:"),
        "fields": [
            (_("Name"), 1),
            (_("Key"), 2),
            (_("Favorite"), 3)
        ],
        "name_text": _("Enter new name:"),
        "key_text": _("Enter new key:"),
        "starred_text": _("Is this project will be a favorite:"),
        "favorites": [(_("True"), True), (_("False"), False)],
        "continue": _("Continue"),
        "cancel": _("Cancel"),
    }
