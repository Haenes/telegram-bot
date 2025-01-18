from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
    Start,
    Back,
    Next,
    Group,
    Cancel
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format, Const

from .states import StartSG, LoginSG, SettingsSG, ProjectsSG
from .getters_and_setters import (
    start_getter,
    process_result,
    login_email_getter,
    login_password_getter,
    login_results_getter,
    settings_getter,
    language_getter,
    language_setter,
    timezone_getter,
    timezone_setter
)

start = Dialog(
    Window(
        Format("{start_text}"),
        Format("{dialog_data[result]}", when="dialog_data"),
        Group(
            Start(Format("{login_btn}"), id="login", state=LoginSG.email),
            Start(Format("{projects_btn}"), id="projects", state=ProjectsSG.projects),
            Start(Format("{settings_btn}"), id="settings", state=SettingsSG.main),
            width=3
        ),
        state=StartSG.start,
        getter=start_getter,
    ),
    on_process_result=process_result
)

login = Dialog(
    Window(
        Format("{email_text}"),
        TextInput(id="email", on_success=Next()),
        state=LoginSG.email,
        getter=login_email_getter
    ),
    Window(
        Format("{password_text}"),
        TextInput(id="password", on_success=Next()),
        state=LoginSG.password,
        getter=login_password_getter
    ),
    Window(
        Format("{results}", when="results"),
        SwitchTo(
            text=Format("{try_again}"),
            id="try_to_login_again_after_error",
            state=LoginSG.email,
            when="try_again"
        ),
        state=LoginSG.results,
        getter=login_results_getter
    ),
)

settings = Dialog(
    Window(
        Format("{settings_text}"),
        Group(
            SwitchTo(Format("{language_btn}"), "lang", SettingsSG.language),
            SwitchTo(Format("{timezone_btn}"), "tz", SettingsSG.timezone),
            Cancel(Const("Back"), "from_settings"),
            width=2
        ),
        state=SettingsSG.main,
        getter=settings_getter,
    ),
    Window(
        Format("{language_text}"),
        Group(
            Button(Format("{en_btn}"), "en", language_setter),
            Button(Format("{ru_btn}"), "ru", language_setter),
            Back(Const("Back"), "from_lang"),
            width=2
        ),
        state=SettingsSG.language,
        getter=language_getter
    ),
    Window(
        Format("{timezone_text}"),
        Group(
            Button(Format("{UTC}"), "UTC", timezone_setter),
            Button(Format("{Moscow}"), "Moscow", timezone_setter),
            Button(Format("{Vladivostok}"), "Vladivostok", timezone_setter),
            width=2
        ),
        SwitchTo(Const("Back"), "from_tz", SettingsSG.main),
        state=SettingsSG.timezone,
        getter=timezone_getter
    ),
)
