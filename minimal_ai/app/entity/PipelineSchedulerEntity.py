from datetime import datetime
from typing import AsyncGenerator

from pydantic import BaseModel, ConfigDict, field_serializer
from sqlalchemy import Result, select

from minimal_ai.app.models.tables import PipelineScheduler
from minimal_ai.app.services.database import BaseRepository


class PipelineSchedulerSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    id: str
    next_run_time: float

    @field_serializer('next_run_time')
    def serialize_dt(self, next_run_time: float):
        return datetime.fromtimestamp(next_run_time).strftime("%Y-%m-%d %H:%M:%S")


class PipelineSchedulerEntity(BaseRepository[PipelineScheduler]):
    schema_class = PipelineScheduler

    async def all(self) -> AsyncGenerator:
        async for instance in self._all():
            yield PipelineSchedulerSchema(**instance.__dict__).model_dump()

    async def get(self, id_: str):
        query = (
            select(PipelineScheduler)
            .where(getattr(self.schema_class, "id") == id_)
        )

        result: Result = await self.execute(query)
        if not (instance := result.scalars().one_or_none()):
            return {"id": None, "next_run_time": None}

        return PipelineSchedulerSchema(**instance.__dict__).model_dump()
