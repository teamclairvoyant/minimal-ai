import logging

from pydantic.dataclasses import dataclass
from pyspark.sql import DataFrame, SparkSession

from minimal_ai.app.services.minimal_exception import MinimalETLException

logger = logging.getLogger(__name__)


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class DataframeUtils:
    """
    Collection of methods related to spark dataframe
    """
    @staticmethod
    async def get_df_from_alias(spark: SparkSession, alias: str) -> DataFrame:
        """
        Method to get the dataframe from the alias name
        @param spark: SparkSession name
        @param alias: alias of the dataframe
        @return: None
        """
        try:
            logger.info("fetching dataframe - %s", alias)
            return spark.sql(f"select * from {alias}")
        except Exception as excep:
            logger.error(str(excep))
            raise MinimalETLException(excep)
