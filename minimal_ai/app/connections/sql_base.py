import logging
from typing import Any, List

from minimal_ai.app.utils.string_utils import clean_query

logger = logging.getLogger(__name__)


class Connection():

    def execute(self, query_string: str, commit=False) -> List[dict]:
        """method to execute the query string"""
        logger.debug("Info connecting to database")
        data: List[dict] = []
        conn = self.build_connection()  # type: ignore

        with conn.cursor() as cursor:
            cursor.execute(clean_query(query_string))
            if cursor.description:
                columns = cursor.column_names
                for row in cursor.fetchall():
                    data.append(dict(zip(columns, row)))

        if commit:
            conn.commit()

        self.close_connection(conn)  # type: ignore

        return data

    def execute_with_cursor(self, query_string: str, curr) -> List[Any]:
        """method to execute the query with the cursor

        Args:
            qury_string (str): query string to be executed
            curr (_type_): cursor object
        """
        logger.debug("Info connecting to database")
        data: List[Any] = []

        curr.execute(clean_query(query_string))
        if curr.description:
            data = curr.fetchall()

        return data
