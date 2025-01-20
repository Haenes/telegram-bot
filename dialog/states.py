from aiogram.filters.state import State, StatesGroup


class StartSG(StatesGroup):
    start = State()


class LoginSG(StatesGroup):
    email = State()
    password = State()
    results = State()


class ProjectsSG(StatesGroup):
    main = State()


class CreateProjectSG(StatesGroup):
    name = State()
    key = State()
    starred = State()
    results = State()


class ProjectSG(StatesGroup):
    details = State()


class EditProjectSG(StatesGroup):
    select = State()
    name = State()
    key = State()
    starred = State()


class IssuesSG(StatesGroup):
    main = State()


class CreateIssueSG(StatesGroup):
    title = State()
    description = State()
    type = State()
    priority = State()
    status = State()


class IssueSG(StatesGroup):
    details = State()


class EditIssueSG(StatesGroup):
    select = State()
    title = State()
    description = State()
    type = State()
    priority = State()
    status = State()


class SettingsSG(StatesGroup):
    main = State()
    language = State()
    timezone = State()
