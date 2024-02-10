from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession,
    create_async_engine
    )
from sqlalchemy.orm import sessionmaker


def make_async_engine(URL: URL | str) -> AsyncEngine:
    return create_async_engine(url=URL, echo=True, pool_pre_ping=True)


async def proceed_schemas(engine: AsyncEngine, metadata) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


def get_sessionmaker(engine=AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession)
