import asyncio
import json
import logging
from typing import Any

from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils.spark_utils import DataframeUtils

# from pyspark.sql.functions import col


logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class SparkTransformer:
    current_task: Any
    spark: SparkSession

    async def transform(self) -> None:
        """method to execute the transformer

        Raises:
            MinimalETLException
        """
        match self.current_task.config["type"]:
            case "join":
                await self.join_df()
            # case "pivot":
            #     return await self.pivot()
            case "filter":
                await self.filter_df()
            case "customsql":
                await self.custom_sql_df()
            case _:
                logger.error(
                    "Transformer type - %s not supported",
                    self.current_task.transformer_type,
                )
                raise MinimalETLException(
                    f"Transformer type - {self.current_task.transformer_type} not supported"
                )

    async def filter_df(self) -> None:
        """method to filter the dataframe on the given condition"""
        try:
            logger.info("Loading data variables from upstream task")
            logger.info("Filtering dataframe on the condition provided")
            _df = await DataframeUtils.get_df_from_alias(
                self.spark,
                self.current_task.upstream_tasks[0],
                self.current_task.config["properties"]["filter"],
            )
            _df.createOrReplaceTempView(self.current_task.uuid)
            asyncio.create_task(
                self.current_task.pipeline.variable_manager.add_variable(
                    self.current_task.pipeline.uuid,
                    self.current_task.uuid,
                    self.current_task.uuid,
                    _df.toJSON().take(200),
                )
            )
        except Exception as excep:
            await self.current_task.pipeline.update_node_reactflow_props(
                self.current_task.uuid, "type", "failNode"
            )
            raise MinimalETLException(f"Failed to filter dataframe - {excep.args}")

    async def custom_sql_df(self) -> None:
        """method to run custom sql query on dataframe"""
        try:
            logger.info("Loading data variables from upstream task")
            logger.info("running query on dataframe")
            _query = str(self.current_task.config["properties"]["query"]).replace(
                ":df", self.current_task.upstream_tasks[0]
            )

            _df = self.spark.sql(_query)

            _df.createOrReplaceTempView(self.current_task.uuid)
            asyncio.create_task(
                self.current_task.pipeline.variable_manager.add_variable(
                    self.current_task.pipeline.uuid,
                    self.current_task.uuid,
                    self.current_task.uuid,
                    _df.toJSON().take(200),
                )
            )
        except Exception as excep:
            await self.current_task.pipeline.update_node_reactflow_props(
                self.current_task.uuid, "type", "failNode"
            )

            raise MinimalETLException(
                f"Failed to execute sql query on dataframe - {excep.args}"
            )

    async def join_df(self) -> None:
        """
        Method to join dataframes from two tasks
        """
        try:
            logger.info("Loading data variables from upstream tasks")
            # left_df = await DataframeUtils.get_df_from_alias(
            #     self.spark, self.current_task.config["properties"]["left_table"]
            # )

            # right_df = await DataframeUtils.get_df_from_alias(
            #     self.spark, self.current_task.config["properties"]["right_table"]
            # )

            # logger.info("Data loaded")
            # left_on = self.current_task.config["properties"]["left_on"].copy()
            # right_on = self.current_task.config["properties"]["right_on"].copy()
            # for index in range(len(left_on)):
            #     if left_on[index] == right_on[index]:
            #         left_df = left_df.withColumnRenamed(
            #             left_on[index],
            #             f'{left_on[index]}_{self.current_task.config["properties"]["left_table"]}',
            #         )
            #         right_df = right_df.withColumnRenamed(
            #             right_on[index],
            #             f'{right_on[index]}_{self.current_task.config["properties"]["right_table"]}',
            #         )
            #         left_on[
            #             index
            #         ] = f'{left_on[index]}_{self.current_task.config["properties"]["left_table"]}'
            #         right_on[
            #             index
            #         ] = f'{right_on[index]}_{self.current_task.config["properties"]["right_table"]}'

            # on = [
            #     col(f) == col(s)
            #     for (f, s) in zip(
            #         self.current_task.config["properties"]["left_on"],
            #         self.current_task.config["properties"]["right_on"],
            #     )
            # ]

            # _df = left_df.join(
            #     right_df,
            #     on=self.current_task.config["properties"]["on"],
            #     how=self.current_task.config["properties"]["how"],
            # )
            select_condn = " ,\n".join(
                [
                    " as ".join([i[1], i[0]])
                    for i in self.current_task.config["properties"][
                        "target_columns"
                    ].items()
                ]
            )

            join_sql = f"""select {select_condn} \nfrom {self.current_task.config["properties"]["left_table"]}
{self.current_task.config["properties"]["how"]} join
{self.current_task.config["properties"]["right_table"]}
on {self.current_task.config["properties"]["on"]}"""

            if {self.current_task.config["properties"]["where"]}:
                join_sql = (
                    join_sql
                    + f'\nwhere {self.current_task.config["properties"]["where"]}'
                )

            _df = self.spark.sql(join_sql)
            _df.createOrReplaceTempView(self.current_task.uuid)

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
        except Exception as excep:
            logger.error(excep)
            await self.current_task.pipeline.update_node_reactflow_props(
                self.current_task.uuid, "type", "failNode"
            )
            raise MinimalETLException(f"Failed to join dataframe - {excep.args}")
