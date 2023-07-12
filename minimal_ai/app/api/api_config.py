import os
import secrets
from typing import Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    """Settings class which extends BaseSettings
    """
    API_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    REPO_PATH: str = os.path.join(os.getcwd())
    PIPELINES_DIR: str = os.path.join(os.getcwd(), 'pipelines')
    LOG_DIR: str = os.path.join(os.getcwd(), 'logs')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

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

    PROJECT_NAME: str = "minimal-ai"
    # scheduler settings
    SCHEDULER_DB_DIR: str = os.path.join(PIPELINES_DIR, 'scheduler')
    THREAD_POOL_EXECUTOR: int = 20
    PROCESS_POOL_EXECUTOR: int = 5

    class Config:
        """
            Config class
        """
        case_sensitive = True


settings = Settings()
