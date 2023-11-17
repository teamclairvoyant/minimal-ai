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
    async def get_df_from_alias(
        spark: SparkSession, alias: str, _filter: str | None = None
    ) -> DataFrame:
        """
        Method to get the dataframe from the alias name
        @param spark: SparkSession name
        @param alias: alias of the dataframe
        @return: None
        """
        try:
            logger.info("fetching dataframe - %s", alias)
            if _filter:
                logger.info("select * from %s where %s", alias, _filter)
                return spark.sql(f"select * from {alias} where {_filter}")
            return spark.sql(f"select * from {alias}")
        except Exception as excep:
            logger.error(str(excep))
            raise MinimalETLException(excep)
