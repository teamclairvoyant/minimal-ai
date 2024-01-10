import logging

from pydantic.dataclasses import dataclass

from minimal_ai.app.services.minimal_exception import MinimalETLException

from .bigquery import BigQuery
from .file_system import FileSchema
from .mysql import MySql

logger = logging.getLogger(__name__)

_connections = {"mysql": MySql, "bigquery": BigQuery, "local_file": FileSchema}


@dataclass
class Connections:
    config: dict

    async def get_schema(self) -> list[dict]:
        """method to resolve source and get schema"""

        if _connections.get(self.config["_type"], None) is None:
            raise MinimalETLException(
                f'support not yet added for - {self.config["_type"]}'
            )
        match self.config["_type"]:
            case "mysql":
                con = MySql(
                    database=self.config["properties"]["database"],
                    host=self.config["properties"]["host"],
                    password=self.config["properties"]["password"],
                    username=self.config["properties"]["user"],
                    port=int(self.config["properties"]["port"]),
                )
                return con.get_information_schema(self.config["properties"]["table"])
            case "local_file":
                con = FileSchema(
                    system=self.config["_type"],
                    file_type=self.config["properties"]["file_type"],
                    file_path=self.config["properties"]["file_path"],
                )

                return con.get_information_schema()
            case _:
                raise MinimalETLException(
                    f'support not yet added for - {self.config["_type"]}'
                )
