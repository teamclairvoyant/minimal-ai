from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///minimalAi.db"

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(bind=engine)  # type:ignore


class Base(DeclarativeBase):
    pass


async def get_db_session():
    """Method to create async db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
