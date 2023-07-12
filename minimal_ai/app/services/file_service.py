import logging
import os
from typing import Dict

import polars as pl

from minimal_ai.app.services.minimal_exception import MinimalETLException

logger = logging.getLogger(__name__)


class FileService:

    @staticmethod
    def load_source(config: Dict, file_path: str) -> pl.DataFrame:
        """
        method to load file source
        Args:
            config (Dict): config of loader
            file_path (str): path of the file

        Returns:
            dataframe
        """
        logger.info("Loading data from file - %s", config['file_name'])
        _final_path = os.path.join(file_path, config['file_name'])

        if not os.path.exists(_final_path):
            logger.error('File path - %s does not exists', _final_path)
            raise MinimalETLException(
                f'File path - {_final_path} does not exists')
        _options = {"separator": ",",
                    "has_header": True}
        match config['file_type']:
            case "csv":
                _df = pl.read_csv(_final_path, **_options)
                logger.debug(_df)
                return _df

            case _:
                logger.error('File type - %s not supported',
                             config['file_type'])
                raise MinimalETLException(
                    f'File type - {config.get("file_type")} not supported')
