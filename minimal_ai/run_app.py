import os

import dotenv
import typer

app = typer.Typer()
dotenv.load_dotenv(os.path.join(os.getcwd(), '.minimalai.env'))


@app.callback()
def callback():
    """main script to initiate and execute minimal_ai
    """


@app.command()
def init_project():
    """command to initialize the project
    """
    from minimal_ai.app.api.api_config import settings
    if not os.path.exists(settings.MINIMAL_AI_REPO_PATH):
        os.makedirs(settings.MINIMAL_AI_REPO_PATH)
        os.makedirs(settings.PIPELINES_DIR)
        os.makedirs(settings.LOG_DIR)
    else:
        if not os.path.exists(settings.PIPELINES_DIR):
            os.makedirs(settings.PIPELINES_DIR)
        if not os.path.exists(settings.LOG_DIR):
            os.makedirs(settings.LOG_DIR)


@app.command()
def run_webserver():
    """command to start the webserver
    """
    from minimal_ai.run_server import start
    start()


# @app.command()
# def check_conn():
#     """checking conn"""
#     conn = BigQuery(dataset="minimal_ai",
#                     path_to_creds_file="/Users/kumar/Downloads/grounded-primer-393415-82e216bd01ad.json")
#     conn.get_information_schema("account_test")


if __name__ == '__main__':
    app()
