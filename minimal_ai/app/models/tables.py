from typing import TypeVar

from sqlalchemy import (Column, DateTime, Enum, Float, Integer, LargeBinary,
                        String, Unicode)
from sqlalchemy.orm import declarative_base

__all__ = ("Base", "PipelineExecution")

Base = declarative_base()

ConcreteTable = TypeVar("ConcreteTable", bound=Base)


class PipelineExecution(Base):
    __tablename__ = "pipeline_execution"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    trigger = Column(Enum('MANUAL', 'SCHEDULED',
                          name='trigger'), nullable=False)
    pipeline_uuid = Column(String, nullable=False)
    execution_date = Column(DateTime, nullable=False)
    status = Column(Enum('COMPLETED', 'FAILED', 'CANCELLED', 'RUNNING',
                    name='runstatus'), nullable=False)


class PipelineScheduler(Base):
    __tablename__ = "pipeline_scheduler"

    id = Column(Unicode(191), primary_key=True)
    next_run_time = Column(Float(25), index=True)
    job_state = Column(LargeBinary, nullable=False)
