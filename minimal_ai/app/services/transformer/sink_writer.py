import logging
from typing import Any, Dict

from pydantic.dataclasses import dataclass
from pyspark.sql import DataFrame, SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils.spark_utils import DataframeUtils

DB_MYSQL_URL: str = "jdbc:mysql://{host}:{port}/{database}"
GS_FILE_PATH = "gs://{bucket_name}/{file_path}"

logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class SparkSinkWriter:
    current_task: Any
    spark: SparkSession

    async def write(self) -> None:
        """method to create writer and write data to sink"""
        logger.info(
            "Configuring sink to write data to - %s",
            self.current_task.config["area"],
        )
        sinks = {
            "warehouse": self.warehouse_writer,
            "local_file": self.local_file_writer,
            "gcp_bucket": self.gs_file_writer,
            "bigquery": self.bigquery_writer,
        }
        writer = sinks.get(self.current_task.config["area"], None)
        if writer is None:
            raise MinimalETLException(
                f'Sink type - {self.current_task.config["area"]} not supported yet'
            )

        await writer()

    async def warehouse_writer(self) -> None:
        """Reader for data warehouses"""
        logger.info(
            "Writing data to - %s", self.current_task.config["properties"]["type"]
        )
        warehouse_type = {"mysql": self.mysql_writer, "bigquery": self.bigquery_writer}
        warehouse_reader = warehouse_type.get(
            self.current_task.config["properties"]["type"], None
        )
        if warehouse_reader is None:
            raise MinimalETLException(
                f'Support for source - {self.current_task.config["properties"]["type"]} not added yet'
            )
        await warehouse_reader()

    async def mysql_writer(self) -> None:
        """method to write the df to rdbms"""
        try:
            logger.info("writing dataframe to - %s", self.current_task.config["area"])

            _url = DB_MYSQL_URL.format(
                host=self.current_task.config["properties"]["host"],
                port=self.current_task.config["properties"]["port"],
                database=self.current_task.config["properties"]["database"],
            )

            _prop: Dict[str, str] = {
                "user": self.current_task.config["properties"]["user"],
                "password": self.current_task.config["properties"]["password"],
            }
            _df: DataFrame = await DataframeUtils.get_df_from_alias(
                self.spark, self.current_task.upstream_tasks[0]
            )
            _df.write.jdbc(
                url=_url,
                table=self.current_task.config["properties"]["table"],
                mode=self.current_task.config["properties"]["mode"],
                properties=_prop,
            )
            logger.info(
                "Dataframe successfully loaded to - %s ",
                self.current_task.config["properties"]["table"],
            )
        except Exception as excep:
            raise MinimalETLException(excep.args)

    async def local_file_writer(self) -> None:
        """method to write the df to file system"""
        try:
            logger.info(
                "writing dataframe to - %s",
                self.current_task.config["properties"]["type"],
            )
            match self.current_task.config["properties"]["type"]:
                case "csv":
                    _options = (
                        self.current_task.config["properties"]["extras"]
                        if self.current_task.config["properties"]["extras"]
                        else {}
                    )
                    _df: DataFrame = await DataframeUtils.get_df_from_alias(
                        self.spark, self.current_task.upstream_tasks[0]
                    )

                    _df.write.csv(
                        path=self.current_task.config["properties"]["file_path"],
                        mode=self.current_task.config["properties"]["mode"],
                        **_options,
                    )
                    logger.info(
                        "Dataframe successfully loaded to - %s ",
                        self.current_task.config["properties"]["file_path"],
                    )

        except Exception as excep:
            raise MinimalETLException(str(excep.args))

    async def gs_file_writer(self) -> None:
        """method to write the df to gs file system"""
        try:
            logger.info(
                "writing dataframe to - %s ",
                self.current_task.config["properties"]["file_type"],
            )

            _df: DataFrame = await DataframeUtils.get_df_from_alias(
                self.spark, self.current_task.upstream_tasks[0]
            )

            match self.current_task.config["properties"]["file_type"]:
                case "csv":
                    _df.write.csv(
                        path=self.current_task.config["properties"]["file_path"],
                        mode=self.current_task.config["properties"]["mode"],
                        sep=",",
                        header=True,
                    )

                case _:
                    logger.error(
                        "File type not supported - %s in sink writer",
                        self.current_task.config["properties"]["file_type"],
                    )
                    raise MinimalETLException(
                        f'File type {self.current_task.config["properties"]["file_type"]} not supported as writer'
                    )

            logger.info(
                "Dataframe successfully loaded to - %s ",
                self.current_task.config["properties"]["file_path"],
            )

        except Exception as excep:
            raise MinimalETLException(str(excep.args))

    async def bigquery_writer(self) -> None:
        """method to write the df to bigquery"""
        try:
            logger.info("writing dataframe to bigqury")
            _df: DataFrame = await DataframeUtils.get_df_from_alias(
                self.spark, self.current_task.upstream_tasks[0]
            )

            _df.write.format("bigquery").option("writeMethod", "direct").mode(
                self.current_task.config["properties"]["mode"]
            ).save(f'{self.current_task.config["properties"]["table"]}')

            logger.info(
                "Dataframe successfully loaded to bigquery at - %s ",
                self.current_task.config["properties"]["table"],
            )

        except Exception as excep:
            raise MinimalETLException(str(excep.args))
