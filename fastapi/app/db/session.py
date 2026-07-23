from collections.abc import AsyncIterator
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

_async_url = settings.database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://")

engine = create_async_engine(
    _async_url,
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


def utcnow() -> datetime:
    return datetime.now(UTC)
