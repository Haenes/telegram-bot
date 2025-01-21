from aiogram.filters.state import State, StatesGroup


class ProjectsSG(StatesGroup):
    main = State()


class CreateProjectSG(StatesGroup):
    name = State()
    key = State()
    starred = State()


class ProjectSG(StatesGroup):
    details = State()


class EditProjectSG(StatesGroup):
    select = State()
    name = State()
    key = State()
    starred = State()
