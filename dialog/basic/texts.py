from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager


async def start(dialog_manager: DialogManager, **kwargs):
    return {"start_text": _(
        """\
            Hello {user}!
            \nA quick introduction to working with me:
            \n1) Login: first step is log in via /login command. Without it, I won't work!
            \n2) Starting menu accessed via /menu command.
            \n3) From menu, you can manage your projects and their issues, and change settings.
            \n<b>Please note that you must already be registered through the website or API. If you don't have an account yet, then you need to create one and only then use me. </b>
        """  # noqa: E501
    ).format(user=dialog_manager.event.from_user.first_name)}


async def login(**kwargs):
    return {
        "email_text": _("Enter email:"),
        "password_text": _("Enter password:"),
    }


async def menu(**kwargs):
    return {
        "menu_text": _("Select what you want to get:"),
        "projects_btn": _("Projects"),
        "settings_btn": _("Settings")
    }


async def settings(**kwargs):
    return {
        "settings_text": _("Choose what you want to change:"),
        "language_btn": _("Language"),
        "timezone_btn": _("Timezone"),
        "language_text": _("Select a language:"),
        "languages": [("English 🇺🇸", "en"), ("Русский 🇷🇺", "ru")],
        "timezone_text": _("Select the time zone:"),
        "timezones": [
            ("UTC", "UTC"),
            (_("Moscow"), "Europe/Moscow"),
            (_("Vladivostok"), "Asia/Vladivostok")
        ]
    }
