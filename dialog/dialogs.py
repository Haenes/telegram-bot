from operator import itemgetter

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
    Start,
    Back,
    Next,
    Group,
    ListGroup,
    ScrollingGroup,
    Multiselect,
    Cancel
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format, Const

from .states import (
    StartSG,
    LoginSG,
    SettingsSG,
    ProjectsSG,
    CreateProjectSG,
    ProjectSG,
    EditProjectSG,
    IssuesSG
)
from .getters_and_setters import (
    start_texts_getter,
    process_result,
    login_email_getter,
    login_password_getter,
    login_results_getter,
    settings_texts_getter,
    language_setter,
    timezone_setter,
    projects_texts_getter,
    projects_getter,
    clicked_starred,
    create_project,
    clicked_project,
    project_texts_getter,
    project_getter,
    clicked_edit_project,
    project_edit_texts_getter,
    is_selected,
    edit_project_selected,
    # edit_project,
    delete_project
)

start = Dialog(
    Window(
        Format("{start_text}"),
        Format("{dialog_data[result]}", when="dialog_data"),
        Group(
            Start(Format("{login_btn}"), id="login", state=LoginSG.email),
            Start(Format("{projects_btn}"), id="projects", state=ProjectsSG.main),
            Start(Format("{settings_btn}"), id="settings", state=SettingsSG.main),
            width=3
        ),
        state=StartSG.start,
    ),
    getter=start_texts_getter,
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


projects = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when project created
        Format("\n{projects_text}", when="projects"),
        Format("{zero_projects}", when="no_projects"),
        Format("{need_log_in}", when="need_log_in"),
        ScrollingGroup(
            ListGroup(
                Button(
                    text=Format("{item[name]}"),
                    id="item",
                    on_click=clicked_project
                ),
                id="projects_list",
                item_id_getter=lambda project: project["id"],
                items="projects"
            ),
            id="projects",
            width=2,
            height=5,
            when="projects",
            hide_on_single_page=True
        ),
        Start(
            text=Format("{create}"),
            id="create_new_project",
            state=CreateProjectSG.name
        ),
        Cancel(Format("{back}")),
        state=ProjectsSG.main,
        getter=projects_getter
    ),
    getter=projects_texts_getter,
    on_process_result=process_result
)

create_new_project = Dialog(
    Window(
        Format("{name_text}"),
        TextInput(id="name", on_success=Next()),
        Cancel(Format("{cancel}")),
        state=CreateProjectSG.name,
    ),
    Window(
        Format("{key_text}"),
        TextInput(id="key", on_success=Next()),
        state=CreateProjectSG.key,
    ),
    Window(
        Format("{starred_text}"),
        Group(
            Button(Format("{true}"), "True", Next(on_click=clicked_starred)),
            Button(Format("{false}"), "False", Next(on_click=clicked_starred))
        ),
        state=CreateProjectSG.starred,
    ),
    Window(
        Format("{results}", when="results"),
        SwitchTo(
            text=Format("{try_again}"),
            id="try_to_create_project_again_after_error",
            state=CreateProjectSG.name,
            when="try_again",
        ),
        state=CreateProjectSG.results,
        getter=create_project
    ),
    getter=projects_texts_getter
)

project = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when project edited
        Format("{project}"),
        Format("{error}", when="error"),
        Group(
            Start(Format("{issues}"), "project_issues", IssuesSG.main),
            Button(Format("{edit}"), "edit_project", clicked_edit_project),
            Button(Format("{delete}"), "delete_project", delete_project),
            Cancel(Format("{back}")),
            width=3
        ),
        getter=project_getter,
        state=ProjectSG.details
    ),
    getter=project_texts_getter,
    on_process_result=process_result
)


edit_project = Dialog(
    Window(
        Format("{instructions}"),
        Multiselect(
            checked_text=Format("✓ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="m_field",
            item_id_getter=itemgetter(1),
            items="fields",
        ),
        Button(
            text=Format("{continue}"),
            id="confirm_select",
            on_click=edit_project_selected,
            when=is_selected
        ),
        Cancel(Format("{cancel}")),
        state=EditProjectSG.select,
    ),
    Window(
        Format("{dialog_data[error_name]}", when="dialog_data"),
        Format("\n{name_text}"),
        TextInput(id="name", on_success=edit_project_selected),
        Cancel(Format("{cancel}")),
        state=EditProjectSG.name,
    ),
    Window(
        Format("{dialog_data[error_key]}", when="dialog_data"),
        Format("\n{key_text}"),
        TextInput(id="key", on_success=edit_project_selected),
        state=EditProjectSG.key,
    ),
    Window(
        Format("{starred_text}"),
        Group(
            Button(Format("{true}"), "True", edit_project_selected),
            Button(Format("{false}"), "False", edit_project_selected)
        ),
        state=EditProjectSG.starred,
    ),
    getter=project_edit_texts_getter
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
            Button(Format("{en_btn}"), "en", language_setter),
            Button(Format("{ru_btn}"), "ru", language_setter),
            Back(Const("Back"), "from_lang"),
            width=2
        ),
        state=SettingsSG.language,
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
    ),
    getter=settings_texts_getter
)
