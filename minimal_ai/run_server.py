import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Tuple

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.api.endpoints import api_router
from minimal_ai.app.app_logger.logger import setup_logging
from minimal_ai.app.services.pipeline_scheduler import get_scheduler

setup_logging(settings.LOG_DIR)
logger = logging.getLogger(__name__)
# logger = CustomizeLogger.make_logger()


@asynccontextmanager
async def lifespan_event(app: FastAPI):
    """method to control the scheduler lifespan with that of app
    """
    logger.info("Initialising scheduler instance")
    scheduler = get_scheduler()

    scheduler.start()

    yield
    scheduler.shutdown()


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


class SinglePageApplication(StaticFiles):
    """Acts similar to the bripkens/connect-history-api-fallback
    NPM package."""

    def __init__(self, directory: os.PathLike, index='index.html') -> None:
        self.index = index

        # set html=True to resolve the index even when no
        # the base path is passed in
        super().__init__(directory=directory, packages=None, html=True, check_dir=True)

    def lookup_path(self, path: str) -> Tuple[str, os.stat_result]:
        """Returns the index file when no match is found.

        Args:
            path (str): Resource path.

        Returns:
            [tuple[str, os.stat_result]]: Always retuens a full path and stat result.
        """
        full_path, stat_result = super().lookup_path(path)

        # if a file cannot be found
        if stat_result is None:
            return super().lookup_path(self.index)  # type: ignore

        return (full_path, stat_result)


app.include_router(api_router, prefix=settings.API_STR)

app.mount(
    path='/',
    app=SinglePageApplication(
        directory=Path(__file__).resolve().parent/"static"),
    name='SPA'
)


def start():
    """
        Launch with `poetry run start-app` at root level
    """
    uvicorn.run("minimal_ai.run_server:app",
                host="0.0.0.0", port=4001, reload=True)


if __name__ == '__main__':
    start()
