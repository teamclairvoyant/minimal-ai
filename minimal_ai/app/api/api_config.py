import os
import secrets
from typing import Union

from pydantic import Field, computed_field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings class which extends BaseSettings
    """
    API_STR: str = Field(default="/api/v1")
    SECRET_KEY: str = Field(default=secrets.token_urlsafe(32))
    MINIMAL_AI_REPO_PATH: str = Field(default=os.path.join(
        os.getcwd(), 'MINIMAL-AI-PROJECT'))

    @computed_field
    @property
    def PIPELINES_DIR(self) -> str:
        return os.path.join(self.MINIMAL_AI_REPO_PATH, "pipelines")

    @computed_field
    @property
    def LOG_DIR(self) -> str:
        return os.path.join(self.MINIMAL_AI_REPO_PATH, "logs")

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["http://localhost:5173"])

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, urls: Union[str, list[str]]) -> Union[list[str], str]:
        """method to assemble the cors origins urls

        Args:
            urls (Union[str, list[str]]): list of urls which needs to be added in cors origins

        Returns:
            Union[list[str], str]
        """
        if isinstance(urls, str) and not urls.startswith("["):
            return [i.strip() for i in urls.split(",")]
        if isinstance(urls, (list, str)):
            return urls
        raise ValueError(urls)

    PROJECT_NAME: str = Field(default="minimal-ai")
    # scheduler settings
    # SCHEDULER_DB_DIR: str = Field(
    #     default=os.path.join(REPO_PATH.default, "scheduler"))
    THREAD_POOL_EXECUTOR: int = Field(default=20)
    PROCESS_POOL_EXECUTOR: int = Field(default=5)
    MINIMAL_ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///minimalAi.sqlite"
    MINIMAL_SYNC_DATABASE_URL: str = "sqlite:///minimalAi.sqlite"
    MINIMAL_SCHEDULER_TABLE: str = "pipeline_scheduler"


settings = Settings()
