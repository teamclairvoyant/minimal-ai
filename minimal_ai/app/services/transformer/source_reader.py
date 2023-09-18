import asyncio
import logging
import os
from typing import Any

from google.cloud import storage
from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from minimal_ai.app.services.minimal_exception import MinimalETLException

DB_MYSQL_URL = "jdbc:mysql://{host}:{port}/{database}"
GS_FILE_PATH = "gs://{bucket_name}/{file_path}"

logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class SparkSourceReaders:
    current_task: Any
    spark: SparkSession

    def rdbms_reader(self) -> None:
        """ registers dataframe from rdbms source

        Args:
            config (dict): database configurations
        """

        match self.current_task.loader_config['db_type']:
            case "mysql":

                url = DB_MYSQL_URL.format(host=self.current_task.loader_config.get('host'),
                                          port=self.current_task.loader_config.get(
                                              'port'),
                                          database=self.current_task.loader_config.get('database'))

                _dict = {"url": url,
                         "driver": "com.mysql.cj.jdbc.Driver",
                         "dbtable": self.current_task.loader_config.get("table"),
                         "user": self.current_task.loader_config.get("user"),
                         "password": self.current_task.loader_config.get("password")}

                _df = self.spark.read.format("jdbc").options(**_dict).load()
                _df = _df.select(*(col(x).alias(x + f"_{self.current_task.uuid}")
                                 for x in _df.columns))
                _df.createOrReplaceTempView(self.current_task.uuid)
                logger.info(
                    "Successfully created data frame from source - %s", self.current_task.loader_config['db_type'])

            case _:
                raise MinimalETLException(
                    f"currently this database {self.current_task.loader_config['db_type']} is not supported")

        asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
            self.current_task.pipeline.uuid,
            self.current_task.uuid,
            self.current_task.uuid,
            _df.toJSON().collect()
        ))

    def local_file_reader(self) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """

        logger.info("Loading data from file - %s",
                    self.current_task.loader_config['file_path'])

        if not os.path.exists(self.current_task.loader_config['file_path']):
            logger.error('File path - %s does not exists',
                         self.current_task.loader_config['file_path'])
            raise MinimalETLException(
                f'File path - {self.current_task.loader_config["file_path"]} does not exists')

        match self.current_task.loader_config['file_type']:
            case "csv":
                _options = {"delimiter": ",",
                            "header": True}

                _df = self.spark.read.options(
                    **_options).csv(self.current_task.loader_config['file_path'])
                _df = _df.select(*(col(x).alias(x + f"_{self.current_task.uuid}")
                                 for x in _df.columns))
                _df.createOrReplaceTempView(self.current_task.uuid)
                logger.info("Successfully created dataframe from CSV - %s",
                            self.current_task.loader_config['file_path'])
            case _:
                raise MinimalETLException(
                    f'File type - {self.current_task.loader_config["file_type"]} not supported')

        asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
            self.current_task.pipeline.uuid,
            self.current_task.uuid,
            self.current_task.uuid,
            _df.toJSON().collect()
        ))

    def gs_file_reader(self) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """

        logger.info("Loading data from file - %s in bucket - %s ",
                    self.current_task.loader_config['file_path'], self.current_task.loader_config['bucket_name'])
        storage_client = storage.Client()
        bucket = storage_client.bucket(
            self.current_task.loader_config['bucket_name'])
        blob_name = self.current_task.loader_config['file_path']

        if not bucket.blob(blob_name).exists(storage_client):
            logger.error('File path - %s does not exists in bucket - %s',
                         self.current_task.loader_config['file_path'], self.current_task.loader_config['bucket_name'])
            raise MinimalETLException(
                f'File path - {self.current_task.loader_config["file_path"]} does not exists')

        match self.current_task.loader_config['file_type']:
            case "csv":
                _options = {"delimiter": ",",
                            "header": True}
                gs_f_path = GS_FILE_PATH.format(
                    bucket_name=self.current_task.loader_config['bucket_name'],
                    file_path=self.current_task.loader_config['file_path'])
                _df = self.spark.read.options(
                    **_options).csv(gs_f_path)
                _df = _df.select(*(col(x).alias(x + f"_{self.current_task.uuid}")
                                 for x in _df.columns))
                _df.createOrReplaceTempView(self.current_task.uuid)
                logger.info("Successfully created dataframe from CSV - %s",
                            gs_f_path)
            case _:
                logger.error('File type - %s not supported',
                             self.current_task.loader_config['file_type'])
                raise MinimalETLException(
                    f'File type - {self.current_task.loader_config["file_type"]} not supported')

        asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
            self.current_task.pipeline.uuid,
            self.current_task.uuid,
            self.current_task.uuid,
            _df.toJSON().collect()
        ))
    def json_file_reader(self) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """
         
        logger.info("Loading data from JSON file - %s",
                     self.current_task.loader_config['file_path'])
        
        if not os.path.exists(self.current_task.loader_config['file_path']):
           logger.error('File path - %s does not exist',
                        self.current_task.loader_config['file_path'])
           raise MinimalETLException(
               f'File path - {self.current_task.loader_config["file_path"]} does not exist')
        
        _options = {"multiline": True} # If JSON file has multiline records
        _df = self.spark.read.options(**_options).json(
            self.current_task.loader_config['file_path'])
        _df = _df.select(*(col(x).alias(x + f"_{self.current_task.uuid}")
                           for x in _df.columns))
        _df.createOrReplaceTempView(self.current_task.uuid)
        logger.info("Successfully created dataframe from JSON - %s",
                    self.current_task.loader_config['file_path'])
        
        asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
            self.current_task.pipeline.uuid,
            self.current_task.uuid,
            self.current_task.uuid,
            _df.toJSON().collect()
        ))