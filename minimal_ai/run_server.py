import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.api.endpoints import api_router
from minimal_ai.app.app_logger.logger import setup_logging
from minimal_ai.app.services.pipeline_scheduler import (get_scheduler_obj,
                                                        start_scheduler,
                                                        stop_scheduler)

REPO_PATH_ENV_VAR = 'MINIMAL_REPO_PATH'

setup_logging(settings.LOG_DIR)
logger = logging.getLogger(__name__)
services = {}


@asynccontextmanager
async def lifespan_event(app: FastAPI):
    """method to control the scheduler lifespan with that of app
    """
    os.environ[REPO_PATH_ENV_VAR] = settings.PIPELINES_DIR
    sys.path.append(os.path.dirname(settings.PIPELINES_DIR))

    logger.info("Initialising scheduler instance")
    services['scheduler'] = get_scheduler_obj()

    start_scheduler(services['scheduler'])

    yield
    stop_scheduler(services['scheduler'])


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_STR}/openapi.json",
    lifespan=lifespan_event
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_STR)


def start():
    """
        Launch with `poetry run start-app` at root level
    """
    uvicorn.run("minimal_ai.run_server:app",
                host="0.0.0.0", port=4001, reload=True)


if __name__ == '__main__':
    start()
