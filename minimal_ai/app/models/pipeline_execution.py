import logging
from typing import Dict

from sqlalchemy import (Column, DateTime, Enum, Integer, String, delete, func,
                        select)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from minimal_ai.app.api.db import Base

logger = logging.getLogger(__name__)


class PipelineExecution(Base):
    __tablename__ = "pipeline_execution"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    trigger = Column(Enum('MANUAL', 'SCHEDULED',
                          name='trigger'), nullable=False)
    pipeline_uuid = Column(String, nullable=False)
    execution_date = Column(DateTime, nullable=False)
    status = Column(Enum('COMPLETED', 'FAILED', 'CANCELLED', 'RUNNING',
                    name='runstatus'), nullable=False)

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):

        transaction = cls(**kwargs)
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @classmethod
    def sync_create(cls, db: Session, **kwargs):
        transaction = cls(**kwargs)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @classmethod
    async def get(cls, db: AsyncSession, _id: int):
        try:
            transaction = await db.get(cls, _id)
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def get_execution_summary(cls, db: AsyncSession, pipeline_uuid: str | None = None) -> Dict[str, int]:
        try:
            _select = select(cls.status, func.count(cls.status).label("total"))

            if pipeline_uuid:
                _select = _select.where(cls.pipeline_uuid == pipeline_uuid)

            _select = _select.group_by(cls.status)

            transaction = await db.execute(_select)

            summaries = transaction.all()
            data = {}
            for summary in summaries:
                data[summary[0]] = summary[1]

            return {
                "COMPLETED": data.get("COMPLETED", 0),
                "FAILED": data.get("FAILED", 0),
                "RUNNING": data.get("RUNNING", 0),
                "CANCELLED": data.get("CANCELLED", 0)
            }
        except NoResultFound:
            return {
                "COMPLETED": 0,
                "FAILED": 0,
                "RUNNING": 0,
                "CANCELLED": 0
            }

    @classmethod
    async def update_status(cls, db: AsyncSession, _id: int, _status: str):
        try:
            transaction = await db.get(cls, _id)
            if transaction:
                transaction.status = _status
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
        except NoResultFound:
            return None
        return transaction

    @classmethod
    def sync_update_status(cls, db: Session, _id: int, _status: str):
        try:
            logger.info(_id)
            transaction = db.get(cls, _id)
            if transaction:
                transaction.status = _status
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def get_all(cls, db: AsyncSession):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def delete_all(cls, db: AsyncSession):
        await db.execute(delete(cls))
        await db.commit()
