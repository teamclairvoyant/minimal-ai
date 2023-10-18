from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from minimal_ai.app.services.database.session import (CTX_SESSION,
                                                      create_session)
from minimal_ai.app.services.minimal_exception import MinimalETLException

__all__ = ("transaction",)


@asynccontextmanager
async def transaction() -> AsyncGenerator[AsyncSession, None]:
    """Use this context manager to perform database transactions. in any coroutine in the source code."""

    session: AsyncSession = create_session()
    CTX_SESSION.set(session)

    try:
        yield session
        await session.commit()
    except Exception as error:
        logger.error(f"Rolling back changes. {error}")
        await session.rollback()
        raise MinimalETLException(error.args)
    finally:
        await session.close()
