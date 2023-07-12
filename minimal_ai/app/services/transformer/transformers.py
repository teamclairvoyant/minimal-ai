import logging
from typing import Any, Dict

import polars as pl
from pydantic.dataclasses import dataclass

from minimal_ai.app.services.minimal_exception import MinimalETLException

logger = logging.getLogger(__name__)


@dataclass
class PythonTransformer:
    current_task: Any

    async def transform(self) -> pl.DataFrame:
        """method to execute the transformer

        Raises:
            MinimalETLException

        Returns:
            pd.DataFrame: transformed dataframe
        """
        match self.current_task.transformer_type:
            case "join":
                return await self.join_df()
            case "pivot":
                return await self.pivot()
            case "filter":
                return await self.filter()
            case _:
                logger.error('Transformer type - %s not supported',
                             self.current_task.transformer_type)
                raise MinimalETLException(
                    f'Transformer type - {self.current_task.transformer_type} not supported')

    async def join_df(self) -> pl.DataFrame:
        """
        Method to join dataframes from two tasks
        Args:
            self (DataTransformerTask): transformer task object

        Returns:
            transformed pandas dataframe
        """
        join_config: Dict = self.current_task.transformer_config.copy()
        logger.info('Loading data variables from upstream tasks')

        left_df: pl.DataFrame = await self.current_task.pipeline.variable_manager.get_variable_data(
            join_config['left_table'])
        right_df: pl.DataFrame = await self.current_task.pipeline.variable_manager.get_variable_data(
            join_config['right_table'])
        logger.info('Data loaded')

        join_config.pop('left_table')

        join_config["suffix"] = '_' + join_config.pop('right_table')

        out_df = left_df.join(right_df, **join_config)
        logger.debug(out_df.columns)
        return out_df

    async def pivot(self) -> pl.DataFrame:
        """method to return the pivoted dataframe

        Returns:
            pivoted dataframe
        """
        pivot_config = self.current_task.transformer_config.copy()
        logger.info('Loading data variable from upstream tasks')
        logger.debug(self.current_task.upstream_tasks[0])
        _df: pl.DataFrame = await self.current_task.pipeline.variable_manager \
            .get_variable_data(self.current_task.upstream_tasks[0])

        logger.info('data loaded')
        out_df = _df.pivot(**pivot_config)

        return out_df

    async def filter(self) -> pl.DataFrame:
        """method to filter the dataframe

        Returns:
            filtered dataframe
        """
        logger.info('Loading data variable from upstream tasks')
        logger.debug(self.current_task.upstream_tasks[0])
        _df: pl.DataFrame = await self.current_task.pipeline.variable_manager \
            .get_variable_data(self.current_task.upstream_tasks[0])
        print(_df)
        sql_context = pl.SQLContext()
        sql_context.register("_df", _df.lazy())
        logger.info('data loaded')
        query_str = f"""select * from _df where {self.current_task.transformer_config['where']}"""
        out_df: pl.DataFrame = sql_context.execute(query_str).collect()
        print(out_df)
        return out_df
