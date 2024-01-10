import io
import logging
import os
from typing import List

import polars as pl
from pydantic.dataclasses import dataclass

from minimal_ai.app.connections.sql_base import Connection
from minimal_ai.app.services.minimal_exception import MinimalETLException

logger = logging.getLogger(__name__)


def dict_to_list(data) -> list[dict]:
    return [
        {"COLUMN_NAME": key, "COLUMN_TYPE": str(value)} for key, value in data.items()
    ]


@dataclass
class FileSchema:
    system: str
    file_type: str
    file_path: str

    def get_information_schema(self) -> list[dict]:
        logger.info("Reading data source - %s", self.file_path)
        match self.system:
            case "local_file":
                match self.file_type:
                    case "csv":
                        df = pl.read_csv(
                            self.file_path, has_header=True, null_values="NULL"
                        )
                        schema = df.schema
                        return dict_to_list(schema)
                    case _:
                        raise MinimalETLException(
                            f"File not supported {self.file_type}"
                        )
            case _:
                raise MinimalETLException(f"Data source not supported {self.system}")
