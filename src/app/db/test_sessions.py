from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app.core.config import settings
from src.app.db.sessions import Base


def get_test_engine_and_sessionmaker() -> tuple[
    AsyncEngine, async_sessionmaker[AsyncSession]
]:
    test_engine: AsyncEngine = create_async_engine(settings.TEST_DB_URL, echo=False)
    test_async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
        test_engine, expire_on_commit=False
    )
    return test_engine, test_async_session_maker


async def init_test_db() -> None:
    test_engine, _ = get_test_engine_and_sessionmaker()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def override_get_session_for_tests() -> AsyncGenerator[AsyncSession, None]:
    _, test_async_session_maker = get_test_engine_and_sessionmaker()
    async with test_async_session_maker() as session:
        yield session
