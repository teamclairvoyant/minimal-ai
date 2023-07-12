import asyncio
import logging
import os
import sys

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.app_logger.logger import setup_logging
from minimal_ai.app.utils import excel_to_json

REPO_PATH_ENV_VAR = 'MINIMAL_REPO_PATH'

setup_logging(settings.LOG_DIR)
logger = logging.getLogger(__name__)

os.environ[REPO_PATH_ENV_VAR] = settings.PIPELINES_DIR
sys.path.append(os.path.dirname(settings.PIPELINES_DIR))

logger.info(settings.PIPELINES_DIR)
if not os.path.exists(settings.PIPELINES_DIR):
    logging.info("creating pipeline directory - %s", settings.PIPELINES_DIR)
    os.makedirs(settings.PIPELINES_DIR)

asyncio.run(excel_to_json.to_json(os.path.join(os.getcwd(), 'metadata.xlsx')))
