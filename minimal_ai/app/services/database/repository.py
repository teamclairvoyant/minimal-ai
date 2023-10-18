from typing import Any, AsyncGenerator, Generic, Type

from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.engine import Result

from minimal_ai.app.models.tables import ConcreteTable
from minimal_ai.app.services.database.session import Session
from minimal_ai.app.services.minimal_exception import MinimalETLException

__all__ = ("BaseRepository",)


class BaseRepository(Session, Generic[ConcreteTable]):
    """This class implements the base interface for working with database
    and makes it easier to work with type annotations.

    The Session class implements the database interaction layer.
    """

    schema_class: Type[ConcreteTable]

    def __init__(self) -> None:
        super().__init__()

        if not self.schema_class:
            raise MinimalETLException(
                "Can not initiate the class without schema_class attribute")

    async def _update(
        self, key: str, value: Any, payload: dict[str, Any]
    ) -> ConcreteTable:
        """Updates an existed instance of the model in the related table.
        If some data is not exist in the payload then the null value will
        be passed to the schema class."""

        query = (
            update(self.schema_class)
            .where(getattr(self.schema_class, key) == value)
            .values(payload)
            .returning(self.schema_class)
        )
        result: Result = await self.execute(query)
        await self._session.flush()

        if not (schema := result.scalar_one_or_none()):
            raise MinimalETLException

        return schema

    async def _get(self, key: str, value: Any) -> ConcreteTable:
        """Return only one result by filters"""

        query = select(self.schema_class).where(
            getattr(self.schema_class, key) == value
        )
        result: Result = await self.execute(query)

        if not (_result := result.scalars().one_or_none()):
            raise MinimalETLException

        return _result

    async def count(self) -> int:
        """method to return count"""
        result: Result = await self.execute(func.count(self.schema_class.id))
        value = result.scalar()

        if not isinstance(value, int):
            raise MinimalETLException(
                "For some reason count function returned not an integer."
                f"Value: {value}"
            )

        return value

    async def _first(self, by: str = "id") -> ConcreteTable:
        result: Result = await self.execute(
            select(self.schema_class).order_by(asc(by)).limit(1)
        )

        if not (_result := result.scalar_one_or_none()):
            raise MinimalETLException

        return _result

    async def _last(self, by: str = "id") -> ConcreteTable:
        result: Result = await self.execute(
            select(self.schema_class).order_by(desc(by)).limit(1)
        )

        if not (_result := result.scalar_one_or_none()):
            raise MinimalETLException

        return _result

    async def _save(self, payload: dict[str, Any]) -> ConcreteTable:
        try:
            schema = self.schema_class(**payload)
            self._session.add(schema)
            await self._session.flush()
            await self._session.refresh(schema)
            return schema
        except self._ERRORS:
            raise MinimalETLException

    async def _all(self) -> AsyncGenerator[ConcreteTable, None]:
        result: Result = await self.execute(select(self.schema_class))
        schemas = result.scalars().all()

        for schema in schemas:
            yield schema

    async def delete(self, id_: int) -> None:
        """method to delete object from table"""
        await self.execute(
            delete(self.schema_class).where(self.schema_class.id == id_)
        )
        await self._session.flush()
