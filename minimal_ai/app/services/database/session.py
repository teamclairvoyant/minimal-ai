from contextvars import ContextVar
from functools import lru_cache

from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.services.minimal_exception import MinimalETLException

__all__ = ("create_engine", "create_session", "CTX_SESSION")


@lru_cache(maxsize=1)
def create_engine() -> AsyncEngine:
    """Create a new async database engine.
    A function result is cached since there is not reason to
    initiate the engine more than once since session is created
    for each separate transaction if needed.
    """

    return create_async_engine(
        settings.MINIMAL_ASYNC_DATABASE_URL, future=True, pool_pre_ping=True, echo=False
    )


def create_session(engine: AsyncEngine | None = None) -> AsyncSession:
    """Creates a new async session to execute SQL queries."""

    return AsyncSession(
        engine or create_engine(), expire_on_commit=False, autoflush=False
    )


CTX_SESSION: ContextVar[AsyncSession] = ContextVar("session", default=create_session())


class Session:
    """The basic class to perform database operations within the session."""

    # All sqlalchemy errors that can be raised
    _ERRORS = (IntegrityError, InvalidRequestError)

    def __init__(self) -> None:
        self._session: AsyncSession = CTX_SESSION.get()

    async def execute(self, query) -> Result:
        """method to execute sql query"""
        try:
            result = await self._session.execute(query)
            return result
        except self._ERRORS:
            raise MinimalETLException
