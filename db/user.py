from sqlalchemy import VARCHAR
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base


class User(Base):
    __tablename__ = "tg_user"

    user_id: Mapped[int] = mapped_column(
        primary_key=True,
        unique=True,
        nullable=False
    )
    user_token: Mapped[str] = mapped_column(
        VARCHAR(255),
        unique=True,
        nullable=False
    )
    language: Mapped[str | None] = mapped_column(VARCHAR(7), default="en")
    timezone: Mapped[str | None] = mapped_column(VARCHAR(30), default="UTC")

    def __str__(self) -> str:
        return f"User: ID={self.user_id}"


async def get_user(user_id: int, session: AsyncSession) -> int | None:
    stmt = select(User.user_id).where(User.user_id == user_id)
    return await session.scalar(stmt)


async def get_token(user_id: int, session: AsyncSession) -> str | None:
    stmt = select(User.user_token).where(User.user_id == user_id)
    return await session.scalar(stmt)


async def get_headers(
    user_id: int,
    session: AsyncSession
) -> dict[str, str] | None:
    token = await get_token(user_id, session)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return None


async def get_user_language(user_id: int, session: AsyncSession) -> str | None:
    stmt = select(User.language).where(User.user_id == user_id)
    return await session.scalar(stmt)


async def get_user_timezone(user_id: int, session: AsyncSession) -> str | None:
    stmt = select(User.timezone).where(User.user_id == user_id)
    return await session.scalar(stmt)
