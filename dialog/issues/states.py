from aiogram.filters.state import State, StatesGroup


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
