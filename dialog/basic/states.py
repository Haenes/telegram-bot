from aiogram.filters.state import State, StatesGroup


class StartSG(StatesGroup):
    main = State()


class MenuSG(StatesGroup):
    main = State()


class LoginSG(StatesGroup):
    email = State()
    password = State()
    result = State()


class SettingsSG(StatesGroup):
    main = State()
    language = State()
    timezone = State()
