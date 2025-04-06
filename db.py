import logging
from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from config import settings

async_db_url = (
    f"postgresql+asyncpg://"
    f"{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_DB}"
)

db_url = (
    f"postgresql://"
    f"{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_DB}"
)


def get_engine():
    engine = create_async_engine(
        async_db_url,
        echo=settings.get("DATABASE_ECHO_MODE", False),
        max_overflow=settings.get("DB_CONN_MAX_OVERFLOW", 50),
        connect_args={"server_settings": {"application_name": settings.PROJECT_NAME}},
    )

    _log = logging.getLogger("sqlalchemy.engine.Engine")
    for handler in list(_log.handlers):
        _log.removeHandler(handler)

    return engine


persistent_engine = get_engine()


def get_sync_engine():
    engine = create_engine(
        db_url,
        echo=settings.get("DATABASE_ECHO_MODE", False),
        max_overflow=settings.get("DB_CONN_MAX_OVERFLOW", 50),
        # connect_args={"server_settings": {"application_name": settings.PROJECT_NAME}},
    )

    _log = logging.getLogger("sqlalchemy.engine.Engine")
    for handler in list(_log.handlers):
        _log.removeHandler(handler)

    return engine


sync_engine = get_sync_engine()


async def get_session() -> AsyncSession:
    async with AsyncSession(persistent_engine) as session, session.begin():
        yield session


get_session_dep: AsyncSession = Depends(get_session)
get_session = asynccontextmanager(get_session)
