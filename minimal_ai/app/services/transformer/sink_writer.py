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

    async def db_writer(self) -> None:
        """method to write the df to rdbms
        """
        try:
            logger.info("writing dataframe to - %s",
                        self.current_task.sink_config["db_type"])
            match self.current_task.sink_config["db_type"]:
                case "mysql":
                    _url = DB_MYSQL_URL.format(host=self.current_task.sink_config["host"],
                                               port=self.current_task.sink_config["port"],
                                               database=self.current_task.sink_config["database"])
                case _:
                    raise NotImplementedError(
                        f"currently this database {self.current_task.sink_config['db_type']} is not supported")

            _prop: Dict[str, str] = {
                "user": self.current_task.sink_config["user"],
                "password": self.current_task.sink_config["password"]
            }
            _df: DataFrame = await DataframeUtils.get_df_from_alias(self.spark, self.current_task.upstream_tasks[0])
            _df.write.jdbc(url=_url, table=self.current_task.sink_config["table"],
                           mode=self.current_task.sink_config["ingestion_type"],
                           properties=_prop)
            logger.info("Dataframe successfully loaded to - %s ",
                        self.current_task.sink_config["table"])
        except Exception as excep:
            raise MinimalETLException(str(excep))

    async def local_file_writer(self) -> None:
        """method to write the df to file system
        """
        try:
            logger.info("writing dataframe to - %s",
                        self.current_task.sink_config["file_type"])
            _df: DataFrame = await DataframeUtils.get_df_from_alias(self.spark, self.current_task.upstream_tasks[0])

            _df.write.csv(
                path=self.current_task.sink_config["file_path"], mode="overwrite", sep=",", header=True)
            logger.info("Dataframe successfully loaded to - %s ",
                        self.current_task.sink_config["file_path"])

        except Exception as excep:
            raise MinimalETLException(str(excep))

    async def gs_file_writer(self) -> None:
        """method to write the df to gs file system
        """
        try:
            logger.info("writing dataframe to - %s ",
                        self.current_task.sink_config["file_type"])

            _df: DataFrame = await DataframeUtils.get_df_from_alias(self.spark, self.current_task.upstream_tasks[0])

            match self.current_task.sink_config["file_type"]:
                case "csv":
                    _df.write.csv(
                        path=self.current_task.sink_config["file_path"],
                        mode=self.current_task.sink_config["mode"], sep=",", header=True)

                case _:
                    logger.error("File type not supported - %s in sink writer",
                                 self.current_task.sink_config["file_type"])
                    raise MinimalETLException(
                        f'File type not supported - {self.current_task.sink_config["file_type"]} in sink writer')

            logger.info("Dataframe successfully loaded to - %s ",
                        self.current_task.sink_config["file_path"])

        except Exception as excep:
            raise MinimalETLException(str(excep))

    async def bigquery_writer(self) -> None:
        """ method to write the df to bigquery
        """
        try:
            logger.info("writing dataframe to bigqury")
            _df: DataFrame = await DataframeUtils.get_df_from_alias(self.spark, self.current_task.upstream_tasks[0])

            _df.write.format("bigquery").option("writeMethod", "direct").mode(self.current_task.sink_config['mode'])\
                .save(f"{self.current_task.sink_config['table']}")

            logger.info("Dataframe successfully loaded to bigquery at - %s ",
                        self.current_task.sink_config["table"])

        except Exception as excep:
            raise MinimalETLException(str(excep))
