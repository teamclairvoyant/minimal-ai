import asyncio
import logging
import os
import sys
import typer
from minimal_ai.app.api.api_config import settings
from minimal_ai.app.app_logger.logger import setup_logging
from minimal_ai.app.utils import excel_to_json
from minimal_ai.app.services import PipelineService


REPO_PATH_ENV_VAR = 'MINIMAL_REPO_PATH'
VARIABLE_DIR = '.variable'


setup_logging(settings.LOG_DIR)
logger = logging.getLogger(__name__)

app = typer.Typer()

os.environ[REPO_PATH_ENV_VAR] = settings.PIPELINES_DIR
sys.path.append(os.path.dirname(settings.PIPELINES_DIR))


@app.callback()
def callback():
    """main script to run and execute minimal_ai
    """

@app.command()
def init_app():
    """command to initialize the project
    """
    logger.info("Creating directory for pipelines")
    if os.path.exists(settings.PIPELINES_DIR):
        logger.info("Directory for pipelines already exists")
    else:
        os.makedirs(settings.PIPELINES_DIR)
        logger.info("Created directory at - %s", settings.PIPELINES_DIR)


@app.command()
def generate_json(excel_file_path: str):
    """command to run the app and generate the metadata.json which is required to execute the pipeline

    Args:
        excel_file_path (str): path to excel file
    """
    asyncio.run(excel_to_json.to_json(excel_file_path))

@app.command()
def exec_pipeline(pipeline_uuid: str):
    """command to execute the pipeline

    Args:
        pipeline_uuid (str): uuid of the pipeline
    """
    asyncio.run(PipelineService.execute_pipeline_by_uuid(pipeline_uuid))

if __name__ == '__main__':
    app()
