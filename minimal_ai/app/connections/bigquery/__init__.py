import logging
import os
from typing import Any, List

from google.cloud.bigquery import Client, dbapi
from google.oauth2 import service_account
from pydantic.dataclasses import dataclass

from minimal_ai.app.connections.sql_base import Connection

logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class BigQuery(Connection):
    dataset: str
    path_to_creds_file: str
    location: str | None = None
    client: Client | None = None

    def __post_init__(self):
        # print(self.path_to_creds_file)
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.path_to_creds_file
        creds = service_account.Credentials.from_service_account_file(
            self.path_to_creds_file, scopes=[
                "https://www.googleapis.com/auth/cloud-platform"]
        )
        self.client = Client(credentials=creds, project=creds.project_id)

    def build_connection(self):
        """method to build thr connection object"""
        return dbapi.Connection(self.client)

    def close_connection(self, connection):
        """method to close db connection"""
        connection.close()

    def get_information_schema(self, table_name: str | None = None) -> List[tuple]:
        """method to get the information schema
        """
        query = f"""
        SELECT
            TABLE_NAME
            , COLUMN_DEFAULT
            , NULL as COLUMN_KEY
            , COLUMN_NAME
            , DATA_TYPE
            , IS_NULLABLE
        FROM {self.dataset}.INFORMATION_SCHEMA.COLUMNS
        """
        if table_name:
            query = f'{query} WHERE TABLE_NAME in (\'{table_name}\')'

        conn = self.build_connection()
        cursor = conn.cursor()
        data = self.execute_with_cursor(query, cursor)

        cursor.close()
        self.close_connection(conn)

        return data
