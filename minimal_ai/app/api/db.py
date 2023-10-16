import contextlib
from typing import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.services.minimal_exception import MinimalETLException

Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None
        self._sync_engine: Engine | None = None
        self._sync_sessionmaker: sessionmaker | None = None

    def init(self):
        """Method to initialize the database manager"""
        self._engine = create_async_engine(settings.MINIMAL_ASYNC_DATABASE_URL)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine)
        self._sync_engine = create_engine(settings.MINIMAL_SYNC_DATABASE_URL)
        self._sync_sessionmaker = sessionmaker(bind=self._sync_engine)

    async def close(self):
        """Method to close the database connection"""
        if self._engine is None or self._sync_engine is None:
            raise MinimalETLException(
                "DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._sync_engine.dispose()
        self._engine = None
        self._sessionmaker = None
        self._sync_engine = None
        self._sync_sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Method to connect to database"""
        if self._engine is None:
            raise MinimalETLException(
                "DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Method to start the database session"""
        if self._sessionmaker is None:
            raise MinimalETLException(
                "DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def sync_session(self) -> Session:
        """method to get the database session"""
        if self._sync_sessionmaker is None:
            raise MinimalETLException(
                "DatabaseSessionManager is not initialized")
        return self._sync_sessionmaker()


sessionmanager = DatabaseSessionManager()


async def get_db():
    """method to get db session"""
    async with sessionmanager.session() as session:
        yield session
