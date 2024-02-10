from sqlalchemy import Column, Integer, VARCHAR, JSON
from sqlalchemy import select

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    # Telegram user id
    user_id = Column(Integer, unique=True, nullable=False, primary_key=True)

    # Bugtracker API token
    user_token = Column(VARCHAR(40), unique=True, nullable=True)

    # Headers for further requests to API
    user_headers = Column(JSON, unique=True, nullable=True)

    # User prefered language in bot
    language = Column(VARCHAR(2), default="en")

    # User prefered timezone in bot
    timezone = Column(VARCHAR(16), default="UTC")

    def __str__(self) -> str:
        return f"User: ID={self.user_id}"


async def get_user(user_id: int, session) -> User:
    stmt = select(User).where(User.user_id == user_id)
    return await session.execute(stmt)


async def get_token(user_id: int, session) -> User:
    stmt = select(User.user_token).where(User.user_id == user_id)
    return await session.execute(stmt)


async def get_headers(user_id: int, session) -> User.user_headers:
    stmt = select(User.user_headers).where(User.user_id == user_id)
    return await session.execute(stmt)


async def get_user_language(user_id: int, session) -> User.language:
    stmt = select(User.language).where(User.user_id == user_id)
    return await session.execute(stmt)


async def get_user_timezone(user_id: int, session) -> User.timezone:
    stmt = select(User.timezone).where(User.user_id == user_id)
    return await session.execute(stmt)
