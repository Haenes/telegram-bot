from operator import itemgetter

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    SwitchTo,
    Start,
    Back,
    Group,
    Select,
    Cancel
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format, Const

from .states import StartSG, MenuSG, LoginSG, SettingsSG
from .texts import start, menu, login, settings
from .handlers import (
    handle_login_input,
    set_language,
    set_timezone
)
from .click_handlers import login_user
from ..projects.states import ProjectsSG
from ..utils import process_result


start = Dialog(
    Window(Format("{start_text}"), state=StartSG.main),
    getter=start
)

login = Dialog(
    Window(
        Format("{email_text}"),
        TextInput(id="email", on_success=handle_login_input),
        state=LoginSG.email,
    ),
    Window(
        Format("{password_text}"),
        TextInput(id="password", on_success=handle_login_input),
        state=LoginSG.password,
    ),
    Window(
        Format("{error}", when="error"),
        Format("{success}", when="success"),
        SwitchTo(
            text=Format("{try_again}"),
            id="try_to_login_again_after_error",
            state=LoginSG.email,
            when="try_again"
        ),
        state=LoginSG.result,
        getter=login_user
    ),
    getter=login
)

menu = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),
        Format("\n{menu_text}"),
        Group(
            Start(Format("{projects_btn}"), id="projects", state=ProjectsSG.main),
            Start(Format("{settings_btn}"), id="settings", state=SettingsSG.main),
            width=2
        ),
        state=MenuSG.main,
    ),
    getter=menu,
    on_process_result=process_result
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
    ),
    Window(
        Format("{language_text}"),
        Group(
            Select(
                text=Format("{item[0]}"),
                id="lang",
                item_id_getter=itemgetter(1),
                items="languages",
                on_click=set_language
            ),
            Back(Const("Back"), "from_lang"),
            width=2
        ),
        state=SettingsSG.language,
    ),
    Window(
        Format("{timezone_text}"),
        Group(
            Select(
                text=Format("{item[0]}"),
                id="tz",
                item_id_getter=itemgetter(1),
                items="timezones",
                on_click=set_timezone
            ),
            width=2
        ),
        SwitchTo(Const("Back"), "from_tz", SettingsSG.main),
        state=SettingsSG.timezone,
    ),
    getter=settings
)
