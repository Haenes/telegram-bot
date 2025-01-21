from operator import itemgetter

from aiogram import F

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Group,
    ListGroup,
    ScrollingGroup,
    Select,
    Multiselect,
    Cancel
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format

from .states import IssuesSG, CreateIssueSG, IssueSG, EditIssueSG
from .texts import issues, create, issue, edit
from .getters import get_issues, get_issue
from .click_handlers import (
    new_dialog_issue,
    new_dialog_edit_issue,
    new_dialog_create_issue,
    create_issue_input,
    create_issue_selected,
    create_issue,
    edit_issue_selected,
    delete_issue,
)
from dialog.utils import process_result, is_selected


issues = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when issue created
        Format("\n{issues_text}", when="issues"),
        Format("\n{zero_issues}", when="no_issues"),
        ScrollingGroup(
            ListGroup(
                Button(
                    text=Format("{item[title]}"),
                    id="issue",
                    on_click=new_dialog_issue
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
            on_click=new_dialog_create_issue,
        ),
        Cancel(Format("{back}")),
        state=IssuesSG.main,
        getter=get_issues
    ),
    getter=issues,
    on_process_result=process_result
)

create_new_issue = Dialog(
    Window(
        Format("{dialog_data[error]}", F["dialog_data"]["error"]),
        Format("{dialog_data[error_title]}", F["dialog_data"]["error_title"]),
        Format("\n{title_text}"),
        TextInput(id="title", on_success=create_issue_input),
        Cancel(Format("{cancel}")),
        state=CreateIssueSG.title,
    ),
    Window(
        Format("{description_text}"),
        TextInput(id="description", on_success=create_issue_input),
        Button(Format("{skip}"), "skip_description", Next()),
        state=CreateIssueSG.description,
    ),
    Window(
        Format("{type_text}"),
        Select(
            text=Format("{item[0]}"),
            id="type",
            item_id_getter=itemgetter(1),
            items="types",
            on_click=create_issue_selected
        ),
        state=CreateIssueSG.type,
    ),
    Window(
        Format("{priority_text}"),
        Group(
            Select(
                text=Format("{item[0]}"),
                id="priority",
                item_id_getter=itemgetter(1),
                items="prioritys",
                on_click=create_issue_selected
            ),
            width=3
        ),
        Button(Format("{skip}"), "skip_priority", Next()),
        state=CreateIssueSG.priority,
    ),
    Window(
        Format("{status_text}"),
        Select(
            text=Format("{item[0]}"),
            id="status",
            item_id_getter=itemgetter(1),
            items="statuses",
            on_click=create_issue_selected
        ),
        Button(Format("{skip}"), "skip_status", create_issue),
        state=CreateIssueSG.status,
    ),
    getter=create
)

issue = Dialog(
    Window(
        Format("{dialog_data[result]}", when="dialog_data"),  # when issue edited
        Format("{issue}"),
        Group(
            Button(Format("{edit}"), "edit_issue", new_dialog_edit_issue),
            Button(Format("{delete}"), "delete_issue", delete_issue),
            Cancel(Format("{back}")),
            width=2
        ),
        getter=get_issue,
        state=IssueSG.details
    ),
    getter=issue,
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
    getter=edit
)
