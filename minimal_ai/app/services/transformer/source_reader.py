import asyncio
import logging
import os
from typing import Any

from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException

DB_MYSQL_URL = "jdbc:mysql://{host}:{port}/{database}"

logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class SparkSourceReaders:
    current_task: Any
    spark: SparkSession

    def bigquery_reader(self) -> None:
        """ registers dataframe from bigquery source
        """

        try:
            logger.info("Reading data from Bigquery table - %s",
                        self.current_task.loader_config['table'])
            _df = self.spark.read.format('bigquery').option(
                'table', self.current_task.loader_config['table']).load()

            _df.createOrReplaceTempView(self.current_task.uuid)

            logger.info("Successfully created data frame from source - %s",
                        self.current_task.loader_config['table'])

            asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
                self.current_task.pipeline.uuid,
                self.current_task.uuid,
                self.current_task.uuid,
                _df.toJSON().take(200)
            ))

        except Exception as excep:
            raise MinimalETLException(
                f"Failed to load data from Bigquery - {self.current_task.loader_config['table']} | {excep.args}")

    def rdbms_reader(self) -> None:
        """ registers dataframe from rdbms source
        """
        try:
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

                    _df = self.spark.read.format(
                        "jdbc").options(**_dict).load()

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
                _df.toJSON().take(200)
            ))

        except Exception as excep:
            raise MinimalETLException(
                f"Failed to read data from - {self.current_task.loader_config['db_type']} | {excep.args}")

    def local_file_reader(self) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """
        try:
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
                _df.toJSON().take(200)
            ))

        except Exception as excep:
            raise MinimalETLException(
                f"Failed to read from {self.current_task.loader_config['file_path']} | {excep.args}")

    def gs_file_reader(self) -> None:
        """ registers dataframe from csv source

        Args:
            config (dict): file configurations
        """
        try:
            logger.info("Loading data from file - %s ",
                        self.current_task.loader_config['file_path'])

            # self.spark._jsc.hadoopConfiguration().set("google.cloud.auth.service.account.json.keyfile",
            #                                           self.current_task.loader_config['key_file'])
            self.spark._jsc.hadoopConfiguration().set(
                'fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')

            match self.current_task.loader_config['file_type']:
                case "csv":
                    _options = {"delimiter": ",",
                                "header": True}

                    _df = self.spark.read.options(
                        **_options).csv(self.current_task.loader_config['file_path'])

                    _df.createOrReplaceTempView(self.current_task.uuid)
                    logger.info("Successfully created dataframe from CSV - %s",
                                self.current_task.loader_config['file_path'])
                case _:
                    logger.error('File type - %s not supported',
                                 self.current_task.loader_config['file_type'])
                    raise MinimalETLException(
                        f'File type - {self.current_task.loader_config["file_type"]} not supported')

            asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
                self.current_task.pipeline.uuid,
                self.current_task.uuid,
                self.current_task.uuid,
                _df.toJSON().take(200)
            ))

        except Exception as excep:
            raise MinimalETLException(
                f"Failed to load from {self.current_task.loader_config['file_path']} | {excep.args}")

    def json_file_reader(self) -> None:
        """ registers dataframe from JSON source
        """

        try:
            logger.info("Loading data from JSON file - %s",
                        self.current_task.loader_config['file_path'])
            
            if not os.path.exists(self.current_task.loader_config['file_path']):
                logger.error('JSON file path - %s does not exist',
                             self.current_task.loader_config['file_path'])
                raise MinimalETLException(
                    f'JSON file path - {self.current_task.loader_config["file_path"]} does not exist')
            
            _df = self.spark.read.json(self.current_task.loader_config['file_path'])

            _df.createOrReplaceTempView(self.current_task.uuid)
            logger.info("Successfully created dataframe from JSON - %s",
                        self.current_task.loader_config['file_path'])
            
            asyncio.create_task(self.current_task.pipeline.variable_manager.add_variable(
                self.current_task.pipeline.uuid,
                self.current_task.uuid,
                self.current_task.uuid,
                _df.toJSON().take(200)
            ))

        except Exception as excep:
            raise MinimalETLException(
                f"Failed to read from {self.current_task.loader_config['file_path']} | {excep.args}")
