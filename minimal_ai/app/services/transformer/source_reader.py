import logging
import os
from typing import Dict

from google.cloud import storage
from pyspark.sql import SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException

DB_MYSQL_URL = 'jdbc:mysql://{host}:{port}/{database}'
GS_FILE_PATH = "gs://{bucket_name}/{file_path}"
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
    def local_file_reader(task_uuid: str, config: Dict, spark: SparkSession) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """

        logger.info("Loading data from file - %s", config['file_path'])

        if not os.path.exists(config['file_path']):
            logger.error('File path - %s does not exists', config['file_path'])
            raise MinimalETLException(
                f'File path - {config["file_path"]} does not exists')
        match config['file_type']:
            case "csv":
                _options = {"delimiter": ",",
                            "header": True}

                spark.read.options(
                    **_options).csv(config['file_path']).createOrReplaceTempView(task_uuid)
                logger.info("Successfully created dataframe from CSV - %s",
                            config['file_path'])
            case _:
                logger.error('File type - %s not supported',
                             config['file_type'])
                raise MinimalETLException(
                    f'File type - {config["file_type"]} not supported')

    @staticmethod
    def gs_file_reader(task_uuid: str, config: Dict, spark: SparkSession) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """

        logger.info("Loading data from file - %s in bucket - %s ",
                    config['file_path'], config['bucket_name'])
        storage_client = storage.Client()
        bucket = storage_client.bucket(config['bucket_name'])
        blob_name = config['file_path'].split('/')[-1]

        if not bucket.blob(blob_name).exists(storage_client):
            logger.error('File path - %s does not exists in bucket - %s',
                         config['file_path'], config['bucket_name'])
            raise MinimalETLException(
                f'File path - {config["file_path"]} does not exists')

        match config['file_type']:
            case "csv":
                _options = {"delimiter": ",",
                            "header": True}
                gs_f_path = GS_FILE_PATH.format(
                    bucket_name=config['bucket_name'], file_path=config['file_path'])
                spark.read.options(
                    **_options).csv(gs_f_path).createOrReplaceTempView(task_uuid)
                logger.info("Successfully created dataframe from CSV - %s",
                            gs_f_path)
            case _:
                logger.error('File type - %s not supported',
                             config['file_type'])
                raise MinimalETLException(
                    f'File type - {config["file_type"]} not supported')
