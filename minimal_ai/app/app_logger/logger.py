import logging
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from minimal_ai.app.api.api_config import settings

_today = datetime.now().strftime("%Y-%m-%d")
logging_config = {
    "path": f"{settings.LOG_DIR}/minimal-app-{_today}.log",
    "filename": "access.log",
    "level": "info",
    "rotation": "7 days",
    "retention": "1 months",
    "format": "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
}


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # log = logger.bind(request_id='app')
        logger.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())


class CustomizeLogger:

    @classmethod
    def make_logger(cls):
        """methof to create logger
        """
        _logger = cls.customize_logging(
            logging_config.get('path'),  # type: ignore
            level=logging_config.get('level'),  # type: ignore
            retention=logging_config.get('retention'),  # type: ignore
            rotation=logging_config.get('rotation'),  # type: ignore
            _format=logging_config.get('format')  # type: ignore
        )
        return _logger

    @classmethod
    def customize_logging(cls,
                          filepath: Path,
                          level: str,
                          rotation: str,
                          retention: str,
                          _format: str
                          ):
        """metod to customize the logger object
        """
        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=_format
        )
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=_format
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ['uvicorn',
                     'uvicorn.error',
                     'fastapi'
                     ]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)
