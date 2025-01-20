from operator import itemgetter

from aiogram import F

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
    Select,
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
    IssuesSG,
    CreateIssueSG,
    IssueSG,
    EditIssueSG
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
    projects_texts,
    create_project_texts,
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
    delete_project,
    clicked_issues,
    clicked_issue,
    clicked_issue_type,
    clicked_issue_priority,
    clicked_issue_status,
    issues_texts,
    issues_getter,
    clicked_create_new_issue,
    create_issue_texts,
    create_issue,
    handle_issue_title,
    issue_texts,
    issue_getter,
    issue_edit_texts,
    edit_issue_selected,
    clicked_edit_issue,
    delete_issue
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
    getter=projects_texts,
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
    getter=create_project_texts
)

project = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when project edited
        Format("{project}"),
        Format("{error}", when="error"),
        Group(
            Button(Format("{issues}"), "project_issues", clicked_issues),
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

issues = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when issue created
        Format("\n{issues_text}", when="issues"),
        Format("{zero_issues}", when="no_issues"),
        ScrollingGroup(
            ListGroup(
                Button(
                    text=Format("{item[title]}"),
                    id="item",
                    on_click=clicked_issue
                ),
                id="issues_list",
                item_id_getter=lambda issue: issue["id"],
                items="issues"
            ),
            id="issues",
            width=2,
            height=5,
            when="issues",
            hide_on_single_page=True
        ),
        Button(
            text=Format("{create}"),
            id="create_new_issue",
            on_click=clicked_create_new_issue,
        ),
        Cancel(Format("{back}")),
        state=IssuesSG.main,
        getter=issues_getter
    ),
    getter=issues_texts,
    on_process_result=process_result
)

create_new_issue = Dialog(
    Window(
        Format("{dialog_data[error]}", F["dialog_data"]["error"]),
        Format("{dialog_data[error_title]}", F["dialog_data"]["error_title"]),
        Format("\n{title_text}"),
        TextInput(id="title", on_success=handle_issue_title),
        Cancel(Format("{cancel}")),
        state=CreateIssueSG.title,
    ),
    Window(
        Format("{description_text}"),
        TextInput(id="description", on_success=Next()),
        Button(Format("{skip}"), "skip_description", Next()),
        state=CreateIssueSG.description,
    ),
    Window(
        Format("{type_text}"),
        Select(
            text=Format("{item[0]}"),
            id="s_issue_type",
            item_id_getter=itemgetter(1),
            items="types",
            on_click=clicked_issue_type
        ),
        state=CreateIssueSG.type,
    ),
    Window(
        Format("{priority_text}"),
        Group(
            Select(
                text=Format("{item[0]}"),
                id="s_issue_priority",
                item_id_getter=itemgetter(1),
                items="prioritys",
                on_click=clicked_issue_priority
            ),
        ),
        Button(Format("{skip}"), "skip_priority", Next()),
        state=CreateIssueSG.priority,
    ),
    Window(
        Format("{status_text}"),
        Select(
            text=Format("{item[0]}"),
            id="s_issue_status",
            item_id_getter=itemgetter(1),
            items="statuses",
            on_click=clicked_issue_status
        ),
        Button(Format("{skip}"), "skip_status", create_issue),
        state=CreateIssueSG.status,
    ),
    getter=create_issue_texts
)

issue = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when issue edited
        Format("{issue}"),
        Group(
            Button(Format("{edit}"), "edit_issue", clicked_edit_issue),
            Button(Format("{delete}"), "delete_issue", delete_issue),
            Cancel(Format("{back}")),
            width=2
        ),
        getter=issue_getter,
        state=IssueSG.details
    ),
    getter=issue_texts,
    on_process_result=process_result
)

edit_issue = Dialog(
    Window(
        Format("{instructions}"),
        Group(
            Multiselect(
                checked_text=Format("✓ {item[0]}"),
                unchecked_text=Format("{item[0]}"),
                id="m_field",
                item_id_getter=itemgetter(1),
                items="fields",
            ),
            width=3
        ),
        Button(
            text=Format("{continue}"),
            id="confirm_select",
            on_click=edit_issue_selected,
            when=is_selected
        ),
        Cancel(Format("{cancel}")),
        state=EditIssueSG.select,
    ),
    Window(
        Format("{dialog_data[error_title]}", F["dialog_data"]["error_title"]),
        Format("{dialog_data[error]}", F["dialog_data"]["error"]),
        Format("\n{title_text}"),
        TextInput(id="title", on_success=edit_issue_selected),
        Cancel(Format("{cancel}")),
        state=EditIssueSG.title,
    ),
    Window(
        Format("{description_text}"),
        TextInput(id="description", on_success=edit_issue_selected),
        state=EditIssueSG.description,
    ),
    Window(
        Format("{type_text}"),
        Select(
            text=Format("{item[0]}"),
            id="type",
            item_id_getter=itemgetter(1),
            items="types",
            on_click=edit_issue_selected
        ),
        state=EditIssueSG.type,
    ),
    Window(
        Format("{priority_text}"),
        Group(
            Select(
                text=Format("{item[0]}"),
                id="priority",
                item_id_getter=itemgetter(1),
                items="prioritys",
                on_click=edit_issue_selected
            ),
            width=3
        ),
        state=EditIssueSG.priority,
    ),
    Window(
        Format("{status_text}"),
        Select(
            text=Format("{item[0]}"),
            id="status",
            item_id_getter=itemgetter(1),
            items="statuses",
            on_click=edit_issue_selected
        ),
        state=EditIssueSG.status,
    ),
    getter=issue_edit_texts
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
