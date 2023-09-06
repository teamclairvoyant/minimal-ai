import logging
from typing import Any, Dict

from langchain.chat_models import ChatOpenAI
from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession
from pyspark_ai import SparkAI

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils.spark_utils import DataframeUtils

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
        match self.current_task.transformer_type:
            case "join":
                await self.join_df()
            case "sparkAI":
                await self.spark_ai_transform()
            # case "pivot":
            #     return await self.pivot()
            # case "filter":
            #     return await self.filter()
            case _:
                logger.error('Transformer type - %s not supported',
                             self.current_task.transformer_type)
                raise MinimalETLException(
                    f'Transformer type - {self.current_task.transformer_type} not supported')

    async def spark_ai_transform(self) -> None:
        """method to transform dataframe using sparkAI
        """
        logger.info("Activating SparkAI")
        spark_ai = SparkAI(llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0),   # type: ignore
                           spark_session=self.spark)
        spark_ai.activate()
        _df = await DataframeUtils.get_df_from_alias(self.spark, self.current_task.upstream_tasks[0])
        _df_ai = spark_ai.transform_df(
            df=_df, desc=self.current_task.transformer_config["prompt"])
        _df_ai.createOrReplaceTempView(self.current_task.uuid)

    async def join_df(self) -> None:
        """
        Method to join dataframes from two tasks
        """
        join_config: Dict = self.current_task.transformer_config.copy()
        logger.info('Loading data variables from upstream tasks')

        left_df = await DataframeUtils.get_df_from_alias(self.spark,
                                                         join_config['left_table'])

        right_df = await DataframeUtils.get_df_from_alias(self.spark,
                                                          join_config['right_table'])

        logger.info('Data loaded')

        join_config.pop('left_table')
        join_config.pop('right_table')

        left_df.join(
            right_df, **join_config).createOrReplaceTempView(self.current_task.uuid)
