import logging
from datetime import datetime

from sqlalchemy import Column, Float, LargeBinary, Unicode, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from minimal_ai.app.api.db import Base

logger = logging.getLogger(__name__)


class PipelineScheduler(Base):
    __tablename__ = "pipeline_scheduler"

    id = Column(Unicode(191), primary_key=True)
    next_run_time = Column(Float(25), index=True)
    job_state = Column(LargeBinary, nullable=False)

    @classmethod
    async def get_next_run_time(cls, db: AsyncSession, _id: str):
        try:
            transaction = await db.execute(select(cls.next_run_time).where(cls.id == _id))
            next_run_time = transaction.scalar()
            if next_run_time:
                return datetime.fromtimestamp(next_run_time).strftime("%Y-%m-%d %H:%M:%S")
        except NoResultFound:
            return None

    @classmethod
    async def get_all(cls, db: AsyncSession):
        return (await db.execute(select(cls))).scalars().all()
