from operator import itemgetter

from aiogram import F

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Start,
    Group,
    ListGroup,
    ScrollingGroup,
    Select,
    Multiselect,
    Cancel
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format

from .states import ProjectsSG, CreateProjectSG, ProjectSG, EditProjectSG
from .texts import projects, create, project, edit
from .getters import get_projects, get_project
from .click_handlers import (
    new_dialog_project,
    new_dialog_edit_project,
    create_project_input,
    create_project_starred,
    delete_project,
    edit_project_selected
)
from dialog.issues.click_handlers import new_dialog_issues
from dialog.utils import process_result, is_selected


projects = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when project created
        Format("\n{projects_text}", when="projects"),
        Format("{zero_projects}", when="no_projects"),
        ScrollingGroup(
            ListGroup(
                Button(
                    text=Format("{item[name]}"),
                    id="project",
                    on_click=new_dialog_project
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
        getter=get_projects
    ),
    getter=projects,
    on_process_result=process_result
)

create_new_project = Dialog(
    Window(
        Format("{dialog_data[error]}", F["dialog_data"]["error"]),
        Format("\n{name_text}"),
        TextInput(id="name", on_success=create_project_input),
        Cancel(Format("{cancel}")),
        state=CreateProjectSG.name,
    ),
    Window(
        Format("{dialog_data[error_key]}", F["dialog_data"]["error_key"]),
        Format("\n{key_text}"),
        TextInput(id="key", on_success=create_project_input),
        state=CreateProjectSG.key,
    ),
    Window(
        Format("{starred_text}"),
        Select(
                text=Format("{item[0]}"),
                id="favorite",
                item_id_getter=itemgetter(1),
                items="favorites",
                type_factory=bool,
                on_click=create_project_starred
            ),
        state=CreateProjectSG.favorite,
    ),
    getter=create
)

project = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when project edited
        Format("{project}"),
        Format("{error}", when="error"),
        Group(
            Button(Format("{issues}"), "project_issues", new_dialog_issues),
            Button(Format("{edit}"), "edit_project", new_dialog_edit_project),
            Button(Format("{delete}"), "delete_project", delete_project),
            Cancel(Format("{back}")),
            width=3
        ),
        getter=get_project,
        state=ProjectSG.details
    ),
    getter=project,
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
        Format("{dialog_data[error]}", when=F["dialog_data"]["error"]),
        Format("\n{name_text}"),
        TextInput(id="name", on_success=edit_project_selected),
        Cancel(Format("{cancel}")),
        state=EditProjectSG.name,
    ),
    Window(
        Format("{dialog_data[error_key]}", when=F["dialog_data"]["error_key"]),
        Format("\n{key_text}"),
        TextInput(id="key", on_success=edit_project_selected),
        state=EditProjectSG.key,
    ),
    Window(
        Format("{starred_text}"),
        Select(
            text=Format("{item[0]}"),
            id="favorite",
            item_id_getter=itemgetter(1),
            items="favorites",
            on_click=edit_project_selected
        ),
        state=EditProjectSG.favorite,
    ),
    getter=edit
)
