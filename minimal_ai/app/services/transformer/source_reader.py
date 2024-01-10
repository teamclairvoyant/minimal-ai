import asyncio
import functools
import json
import logging
import os
from typing import Any

import aiofiles
from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils import clean_name

DB_MYSQL_URL = "jdbc:mysql://{host}:{port}/{database}"

logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class SparkSourceReaders:
    current_task: Any
    spark: SparkSession

    async def read(self) -> None:
        """Method to read data from source"""
        logger.info(
            "Configuring reader to read data from - %s",
            self.current_task.config["area"],
        )
        sources = {
            "warehouse": self.warehouse_reader,
            "local_file": self.local_file_reader,
            "gcp_bucket": self.gs_file_reader,
            "bigquery": self.bigquery_reader,
        }
        reader = sources.get(self.current_task.config["area"], None)
        if reader is None:
            raise MinimalETLException(
                f'Support for source - {self.current_task.config["area"]} not added yet'
            )
        await reader()

    async def warehouse_reader(self) -> None:
        """Reader for data warehouses"""
        logger.info(
            "Reading data from - %s", self.current_task.config["properties"]["type"]
        )
        warehouse_type = {"mysql": self.mysql_reader, "bigquery": self.bigquery_reader}
        warehouse_reader = warehouse_type.get(
            self.current_task.config["properties"]["type"], None
        )
        if warehouse_reader is None:
            raise MinimalETLException(
                f'Support for source - {self.current_task.config["properties"]["type"]} not added yet'
            )
        await warehouse_reader()

    async def bigquery_reader(self) -> None:
        """registers dataframe from bigquery source"""

        logger.info(
            "Reading data from Bigquery table - %s",
            self.current_task.config["properties"]["table"],
        )
        _df = (
            self.spark.read.format("bigquery")
            .option("table", self.current_task.config["properties"]["table"])
            .load()
        )

        _df = functools.reduce(
            lambda _df, idx: _df.withColumnRenamed(
                list(_df.schema.names)[idx],
                clean_name(list(_df.schema.names)[idx]) + "_" + self.current_task.uuid,
            ),
            range(len(list(_df.schema.names))),
            _df,
        )

        _df.createOrReplaceTempView(self.current_task.uuid)

        logger.info(
            "Successfully created data frame from source - %s",
            self.current_task.config["properties"]["table"],
        )

        asyncio.create_task(
            self.current_task.pipeline.variable_manager.add_variable(
                self.current_task.pipeline.uuid,
                self.current_task.uuid,
                self.current_task.uuid,
                json.loads(_df.schema.json()),
                _df.count(),
                _df.toJSON().take(200),
            )
        )

    async def mysql_reader(self) -> None:
        """registers dataframe from mysql source"""

        url = DB_MYSQL_URL.format(
            host=self.current_task.config["properties"].get("host"),
            port=self.current_task.config["properties"].get("port"),
            database=self.current_task.config["properties"].get("database"),
        )

        _dict = {
            **(
                self.current_task.config["properties"]["extras"]
                if self.current_task.config["properties"]["extras"]
                else {}
            ),
        }

        _df = self.spark.read.options(**_dict).jdbc(
            url=url,
            table=self.current_task.config["properties"].get("table"),
            properties={
                "user": self.current_task.config["properties"].get("user"),
                "password": self.current_task.config["properties"].get("password"),
            },
        )

        _df = functools.reduce(
            lambda _df, idx: _df.withColumnRenamed(
                list(_df.schema.names)[idx],
                clean_name(list(_df.schema.names)[idx]) + "_" + self.current_task.uuid,
            ),
            range(len(list(_df.schema.names))),
            _df,
        )

        _df.createOrReplaceTempView(self.current_task.uuid)

        logger.info(
            "Successfully created data frame from source - %s",
            self.current_task.config["properties"]["table"],
        )

        asyncio.create_task(
            self.current_task.pipeline.variable_manager.add_variable(
                self.current_task.pipeline.uuid,
                self.current_task.uuid,
                self.current_task.uuid,
                json.loads(_df.schema.json()),
                _df.count(),
                _df.toJSON().take(200),
            )
        )

    async def local_file_reader(self) -> None:
        """registers dataframe from csv source

        Args:
            config (dict): file configurations
        """

        logger.info(
            "Loading data from file - %s",
            self.current_task.config["properties"]["file_path"],
        )

        if not os.path.exists(self.current_task.config["properties"]["file_path"]):
            logger.error(
                "File path - %s does not exists",
                self.current_task.config["properties"]["file_path"],
            )
            raise MinimalETLException(
                f'File path - {self.current_task.config["properties"]["file_path"]} does not exists'
            )

        _options = (
            self.current_task.config["properties"]["extras"]
            if self.current_task.config["properties"]["extras"]
            else {}
        )

        match self.current_task.config["properties"]["type"]:
            case "csv":
                _df = self.spark.read.options(**_options).csv(
                    self.current_task.config["properties"]["file_path"]
                )

            case "json":
                async with aiofiles.open(
                    self.current_task.config["properties"]["file_path"], mode="r"
                ) as fp:
                    json_data = json.loads(await fp.read())
                _df = self.spark.read.options(**_options).json(
                    self.spark.sparkContext.parallelize(json_data)
                )

            case "parquet":
                _df = self.spark.read.options(**_options).parquet(
                    self.current_task.config["properties"]["file_path"]
                )

            case _:
                raise MinimalETLException(
                    f'File type - {self.current_task.config["properties"]["type"]} not supported'
                )

        _df = functools.reduce(
            lambda _df, idx: _df.withColumnRenamed(
                list(_df.schema.names)[idx],
                clean_name(list(_df.schema.names)[idx]) + "_" + self.current_task.uuid,
            ),
            range(len(list(_df.schema.names))),
            _df,
        )

        _df.createOrReplaceTempView(self.current_task.uuid)

        await self.current_task.pipeline.variable_manager.add_variable(
            self.current_task.pipeline.uuid,
            self.current_task.uuid,
            self.current_task.uuid,
            json.loads(_df.schema.json()),
            _df.count(),
            _df.toJSON().take(200),
        )

    async def gs_file_reader(self) -> None:
        """registers dataframe from csv source

        Args:
            config (dict): file configurations
        """

        logger.info(
            "Loading data from file - %s ",
            self.current_task.config["properties"]["file_path"],
        )

        # self.spark._jsc.hadoopConfiguration().set("google.cloud.auth.service.account.json.keyfile",
        #                                           self.current_task.config['key_file'])
        self.spark._jsc.hadoopConfiguration().set(  # type: ignore
            "fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
        )

        match self.current_task.config["properties"]["type"]:
            case "csv":
                _options = {"delimiter": ",", "header": True}

                _df = self.spark.read.options(**_options).csv(
                    self.current_task.config["properties"]["file_path"]
                )

                _df = functools.reduce(
                    lambda _df, idx: _df.withColumnRenamed(
                        list(_df.schema.names)[idx],
                        clean_name(list(_df.schema.names)[idx])
                        + "_"
                        + self.current_task.uuid,
                    ),
                    range(len(list(_df.schema.names))),
                    _df,
                )

                _df.createOrReplaceTempView(self.current_task.uuid)

                logger.info(
                    "Successfully created dataframe from CSV - %s",
                    self.current_task.config["properties"]["file_path"],
                )
            case _:
                logger.error(
                    "File type - %s not supported",
                    self.current_task.config["properties"]["type"],
                )
                raise MinimalETLException(
                    f'File type - {self.current_task.config["properties"]["type"]} not supported'
                )

        asyncio.create_task(
            self.current_task.pipeline.variable_manager.add_variable(
                self.current_task.pipeline.uuid,
                self.current_task.uuid,
                self.current_task.uuid,
                json.loads(_df.schema.json()),
                _df.count(),
                _df.toJSON().take(200),
            )
        )
