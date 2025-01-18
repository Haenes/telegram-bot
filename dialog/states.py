from aiogram.filters.state import State, StatesGroup


class StartSG(StatesGroup):
    start = State()


class LoginSG(StatesGroup):
    email = State()
    password = State()
    results = State()


class ProjectsSG(StatesGroup):
    projects = State()


class SettingsSG(StatesGroup):
    main = State()
    language = State()
    timezone = State()
