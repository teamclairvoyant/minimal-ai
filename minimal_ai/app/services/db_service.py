import logging

import pandas as pd
import polars as pl
import sqlalchemy as sqlal
from sqlalchemy.engine import Engine

from minimal_ai.app.services.minimal_exception import MinimalETLException

DB_MYSQL_URL = 'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'

logger = logging.getLogger(__name__)


class DBService:

    @staticmethod
    def get_db_conn(config: dict) -> Engine:
        """ returns db url

        Args:
            config (dict): database configurations

        Returns:
            str: db url
        """
        match config['db_type']:
            case "mysql":

                url = DB_MYSQL_URL.format(username=config.get('user'),
                                          password=config.get('password'),
                                          host=config.get('host'),
                                          port=config.get('port'),
                                          database=config.get('database'))

                return sqlal.create_engine(url)
            case _:
                raise NotImplementedError(
                    f"currently this database {config['db_type']} is not supported")

    @staticmethod
    def load_source(db_conn: Engine, table: str) -> pl.DataFrame:
        """ method to load the source

        Args:
            db_conn (Engine): database connection
            table (str): name of the table
        """
        logger.info("Fetching data from table - %s", table)
        query = f'select * from {table} '
        query = sqlal.text(query)
        _df = pd.read_sql_query(con=db_conn.connect(), sql=query)
        return pl.from_pandas(_df, include_index=True)

    @staticmethod
    def ingest_data(db_conn: Engine, table: str, data: pd.DataFrame, ingestion_type: str):
        """
        method to ingest data into target
        Args:
            db_conn (Engine): database connection
            table (str): name of the table
            data (dataframe): data to be ingested
            ingestion_type (str): type of ingestion
        """
        try:
            logger.info("Ingesting data into table - %s", table)
            match ingestion_type:
                case "overwrite":
                    data.to_sql(table, db_conn, if_exists="replace",
                                index=True, chunksize=100000)
                case "append":
                    data.to_sql(table, db_conn, if_exists="append",
                                index=False, chunksize=100000)
                case _:
                    logger.error(
                        'Ingestion type - %s not supported', ingestion_type)
                    raise MinimalETLException(
                        f"Ingestion type - {ingestion_type} not supported")
        except Exception as excep:
            logger.error(
                'Failed to ingest data into table - %s', table)
            raise MinimalETLException(
                f"Failed to ingest data into table - {table}", excep.args)
