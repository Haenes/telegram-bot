from aiogram.filters.state import State, StatesGroup


class StartSG(StatesGroup):
    start = State()


class LoginSG(StatesGroup):
    email = State()
    password = State()
    results = State()


# TODO: Remove all create states and use separate CreateProjectSG.
class ProjectsSG(StatesGroup):
    main = State()
    create_name = State()
    create_key = State()
    create_starred = State()
    create_results = State()


class CreateProjectSG(StatesGroup):
    name = State()
    key = State()
    starred = State()
    results = State()


class ProjectSG(StatesGroup):
    details = State()


class EditProjectSG(StatesGroup):
    name = State()
    key = State()
    starred = State()
    results = State()


class IssuesSG(StatesGroup):
    main = State()


class CreateIssueSG(StatesGroup):
    title = State()
    description = State()
    type = State()
    priority = State()
    status = State()


class EditIssueSG(StatesGroup):
    title = State()
    description = State()
    type = State()
    priority = State()
    status = State()


class SettingsSG(StatesGroup):
    main = State()
    language = State()
    timezone = State()
