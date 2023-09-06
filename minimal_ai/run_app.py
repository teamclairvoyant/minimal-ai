import asyncio
import os
import sys

import typer

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.connections.bigquery import BigQuery
from minimal_ai.app.services import PipelineService
from minimal_ai.app.utils import excel_to_json
from minimal_ai.run_server import start

REPO_PATH_ENV_VAR = 'MINIMAL_REPO_PATH'
VARIABLE_DIR = '.variable'


app = typer.Typer()

os.environ[REPO_PATH_ENV_VAR] = settings.PIPELINES_DIR
sys.path.append(os.path.dirname(settings.PIPELINES_DIR))


@app.callback()
def callback():
    """main script to initiate and execute minimal_ai
    """


@app.command()
def init_project():
    """command to initialize the project
    """

    if not os.path.exists(settings.REPO_PATH):
        os.makedirs(settings.REPO_PATH)
        os.makedirs(settings.PIPELINES_DIR)
        os.makedirs(settings.LOG_DIR)


@app.command()
def run_webserver():
    """command to start the webserver
    """
    start()


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


@app.command()
def check_conn():
    """checking conn"""
    conn = BigQuery(dataset="minimal_ai",
                    path_to_creds_file="/Users/kumar/Downloads/grounded-primer-393415-82e216bd01ad.json")
    conn.get_information_schema("account_test")


if __name__ == '__main__':
    app()
