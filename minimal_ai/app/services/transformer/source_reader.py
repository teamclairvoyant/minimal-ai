import logging
import os
from typing import Dict

from pyspark.sql import SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException

DB_MYSQL_URL = 'jdbc:mysql://{host}:{port}/{database}'

logger = logging.getLogger(__name__)


class SparkSourceReaders:

    @staticmethod
    def rdbms_reader(task_uuid: str, config: Dict, spark: SparkSession) -> None:
        """ registers dataframe from rdbms source

        Args:
            config (dict): database configurations
        """

        match config['db_type']:
            case "mysql":

                url = DB_MYSQL_URL.format(host=config.get('host'),
                                          port=config.get('port'),
                                          database=config.get('database'))

                _dict = {"url": url,
                         "driver": "com.mysql.cj.jdbc.Driver",
                         "dbtable": config.get("table"),
                         "user": config.get("user"),
                         "password": config.get("password")}

                _df = spark.read.format("jdbc").options(**_dict).load()

                _df.createOrReplaceTempView(task_uuid)
                logger.info(
                    "Successfully created data frame from source - %s", config['db_type'])

            case _:
                raise NotImplementedError(
                    f"currently this database {config['db_type']} is not supported")

    @staticmethod
    def csv_reader(task_uuid: str, config: Dict, spark: SparkSession, file_path: str) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): database configurations
        """

        logger.info("Loading data from file - %s", config['file_name'])
        _final_path = os.path.join(file_path, config['file_name'])

        if not os.path.exists(_final_path):
            logger.error('File path - %s does not exists', _final_path)
            raise MinimalETLException(
                f'File path - {_final_path} does not exists')

        _options = {"delimiter": ",",
                    "header": True}

        spark.read.options(
            **_options).csv(_final_path).createOrReplaceTempView(task_uuid)
        logger.info("Successfully created dataframe from CSV - %s",
                    config['file_name'])