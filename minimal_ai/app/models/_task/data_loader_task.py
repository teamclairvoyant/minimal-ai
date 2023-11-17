import logging

from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.connections import BigQuery, MySql
from minimal_ai.app.models._task.base import _Task
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.transformer.source_reader import SparkSourceReaders
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass
class DataLoaderTask(_Task):
    def __post_init__(self):
        if not self.config:
            self.config = {"_type": None, "properties": {}, "columns": []}
        self.upstream_tasks = [] if self.upstream_tasks is None else self.upstream_tasks
        self.downstream_tasks = (
            [] if self.downstream_tasks is None else self.downstream_tasks
        )

    @classmethod
    async def create(
        cls,
        name: str,
        task_type: str,
        pipeline=None,
        priority: int | None = None,
        upstream_task_uuids=None,
    ) -> None:
        """method to add task to a pipeline

        Args:
            name (str): task name
            task_type (TaskType): type of the task
            pipeline (Pipeline, optional): pipeline. Defaults to None.
            priority (int | None, optional): priority of the task in the pipeline. Defaults to None.
            upstream_task_uuids (_type_, optional): _description_. Defaults to None.
        """
        if upstream_task_uuids is None:
            upstream_task_uuids = []

        uuid = clean_name(name)
        logger.info("Creating task - %s", uuid)
        if pipeline is not None and pipeline.has_task(uuid):
            logger.error(
                "Task - %s already present in pipeline - %s", uuid, pipeline.uuid
            )
            raise MinimalETLException(
                f"Task {uuid} already exists. Please use a different name."
            )

        logger.info("Task - %s is of type %s", uuid, task_type)

        task = DataLoaderTask(
            uuid=uuid, name=name, task_type=TaskType(task_type), pipeline=pipeline
        )

        await task.after_create(
            pipeline=pipeline,
            priority=priority,
            upstream_task_uuids=upstream_task_uuids,
        )

    async def get_schema(self) -> list[dict]:
        """method to fetch the column list for the task"""
        _connections = {"mysql": MySql, "bigquery": BigQuery, "local_file": ""}
        try:
            logger.info("fetching schema from source - %s", self.config["_type"])
            if self.config["_type"]:
                conn = _connections[self.config["_type"]](
                    database=self.config["properties"]["database"],
                    host=self.config["properties"]["host"],
                    password=self.config["properties"]["password"],
                    username=self.config["properties"]["user"],
                    port=int(self.config["properties"]["port"]),
                )

                return conn.get_information_schema(self.config["properties"]["table"])
            raise MinimalETLException("unable to fetch schema")
        except Exception as excep:
            logger.error("error while fetching schema - %s", excep.args)
            raise MinimalETLException(excep.args)

    async def validate_configurations(self, loader_type: str, loader_config: dict):
        """method to configure task loader

        Args:
            loader_type (str): type of the loader
            loader_config (Dict): properties of the loader

        """
        try:
            loader = LoaderType(loader_type)

            match loader:
                case "mysql":
                    _config = DBConfig.model_validate(loader_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s loader for task - %s", loader_type, self.uuid
                    )
                    self.config["_type"] = loader
                    self.config["properties"] = _config.model_dump()

                case "local_file":
                    _config = FileConfig.model_validate(loader_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s loader for task - %s", loader_type, self.uuid
                    )
                    self.config["_type"] = loader
                    self.config["properties"] = _config.model_dump()

                case "gcp_bucket":
                    _config = GSFileConfig.model_validate(loader_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s loader for task - %s", loader_type, self.uuid
                    )
                    self.config["_type"] = loader
                    self.config["properties"] = _config.model_dump()

                case "bigquery":
                    _config = BigQueryConfig.model_validate(loader_config)
                    logger.info(
                        "Configuring %s sink for task - %s", loader_type, self.uuid
                    )
                    self.config["_type"] = loader
                    self.config["properties"] = _config.model_dump()

                case _:
                    logger.error("Loader type - %s not supported", loader_type)
                    raise MinimalETLException(
                        f"Loader type - {loader_type} not supported"
                    )
        except Exception as excep:
            logger.error("Loader type - %s not supported | %s", loader_type, excep.args)
            raise MinimalETLException(
                f"Loader type - {loader_type} not supported | {excep.args}"
            )

    async def execute(self, spark: SparkSession) -> dict:
        """
        async method to execute the task
        Args:
            spark (SparkSession): current spark session object

        """
        logger.info("Executing task - %s", self.uuid)

        if not self.all_upstream_task_executed:
            self.status = TaskStatus.FAILED
            await self.pipeline.update_node_reactflow_props(
                self.uuid, "type", "failNode"
            )
            logger.error(
                "Not all upstream tasks have been executed. Please execute them first"
            )
            raise MinimalETLException(
                "Not all upstream tasks have been executed. Please execute them first"
            )

        match self.config["type"]:
            case "mysql":
                await SparkSourceReaders(self, spark).rdbms_reader()

            case "local_file":
                await SparkSourceReaders(self, spark).local_file_reader()

            case "gcp_bucket":
                await SparkSourceReaders(self, spark).gs_file_reader()

            case "bigquery":
                await SparkSourceReaders(self, spark).bigquery_reader()

            case _:
                self.status = TaskStatus.FAILED
                logger.error("Loader type - %s not supported", self.config["type"])
                raise MinimalETLException(
                    f'Loader type - {self.config["type"]} not supported'
                )

        self.status = TaskStatus.EXECUTED
        await self.pipeline.update_node_reactflow_props(
            self.uuid, "type", "successNode"
        )
        return {"task": await self.base_dict_obj(), "executed": self.status}
