from datetime import datetime
from typing import Any, AsyncGenerator, Dict

from pydantic import BaseModel, ConfigDict, field_serializer
from sqlalchemy import Result, func, select
from sqlalchemy.exc import NoResultFound

from minimal_ai.app.models.tables import PipelineExecution
from minimal_ai.app.services.database import BaseRepository


class PipelineExecutionSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    id: int
    trigger: str
    pipeline_uuid: str
    execution_date: datetime
    status: str

    @field_serializer("execution_date")
    def serialize_dt(self, execution_date: datetime):
        return execution_date.strftime("%Y-%m-%d %H:%M:%S")


class PipelineExecutionEntity(BaseRepository[PipelineExecution]):
    schema_class = PipelineExecution

    async def all(self) -> AsyncGenerator:
        async for instance in self._all():
            yield PipelineExecutionSchema(**instance.__dict__).model_dump()

    async def get(self, id_: int):
        query = select(PipelineExecution).where(getattr(self.schema_class, "id") == id_)

        result: Result = await self.execute(query)

        if not (instance := result.scalars().one_or_none()):
            return {
                "id": None,
                "trigger": None,
                "pipeline_uuid": None,
                "execution_date": None,
                "status": None,
            }

        return PipelineExecutionSchema(**instance.__dict__).model_dump()

    async def create(self, schema):
        instance = await self._save(schema)
        return PipelineExecutionSchema(**instance.__dict__).model_dump()

    async def update(self, key: str, value: Any, payload: dict[str, Any]):
        instance = await self._update(key, value, payload)
        return PipelineExecutionSchema(**instance.__dict__).model_dump()

    async def get_execution_summary(
        self, pipeline_uuid: str | None = None
    ) -> Dict[str, int]:
        try:
            _select = select(
                self.schema_class.status,
                func.count(self.schema_class.status).label("total"),
            )

            if pipeline_uuid:
                _select = _select.where(
                    self.schema_class.pipeline_uuid == pipeline_uuid
                )

            _select = _select.group_by(self.schema_class.status)

            transaction = await self.execute(_select)

            summaries = transaction.all()
            data = {}
            for summary in summaries:
                data[summary[0]] = summary[1]

            return {
                "COMPLETED": data.get("COMPLETED", 0),
                "FAILED": data.get("FAILED", 0),
                "RUNNING": data.get("RUNNING", 0),
                "CANCELLED": data.get("CANCELLED", 0),
            }
        except NoResultFound:
            return {"COMPLETED": 0, "FAILED": 0, "RUNNING": 0, "CANCELLED": 0}
