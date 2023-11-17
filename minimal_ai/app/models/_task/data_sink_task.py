import logging

from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.models._task.base import _Task
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.transformer.sink_writer import SparkSinkWriter
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass
class DataSinkTask(_Task):
    def __post_init__(self):
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

        task = DataSinkTask(
            uuid=uuid, name=name, task_type=TaskType(task_type), pipeline=pipeline
        )

        await task.after_create(
            pipeline=pipeline,
            priority=priority,
            upstream_task_uuids=upstream_task_uuids,
        )

    async def validate_configurations(self, sink_type: str, sink_config: dict):
        """method to configure task loader

        Args:
            sink_type (str): type of the sink
            sink_config (Dict): properties of the sink

        """

        try:
            match SinkType(sink_type):
                case "rdbms":
                    _config = DBConfig.model_validate(sink_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s sink for task - %s", sink_type, self.uuid
                    )
                    self.config["_type"] = SinkType(sink_type)
                    self.config["properties"] = _config.model_dump()

                case "local_file":
                    _config = FileConfig.model_validate(sink_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s sink for task - %s", sink_type, self.uuid
                    )
                    self.config["_type"] = SinkType(sink_type)
                    self.config["properties"] = _config.model_dump()

                case "gcp_bucket":
                    _config = GSFileConfig.model_validate(sink_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s sink for task - %s", sink_type, self.uuid
                    )
                    self.config["_type"] = SinkType(sink_type)
                    self.config["properties"] = _config.model_dump()

                case "bigquery":
                    _config = BigQueryConfig.model_validate(sink_config)
                    logger.info(
                        "Configuring %s sink for task - %s", sink_type, self.uuid
                    )
                    self.config["_type"] = SinkType(sink_type)
                    self.config["properties"] = _config.model_dump()

                case _:
                    logger.error("Sink type - %s not supported", sink_type)
                    raise MinimalETLException(f"Sink type - {sink_type} not supported")
        except Exception as excep:
            logger.error("Sink type - %s not supported | %s", sink_type, excep.args)
            raise MinimalETLException(
                f"Sink type - {sink_type} not supported | {excep.args}"
            )

    async def execute(self, spark: SparkSession) -> dict:
        """method to execute task

        Args:
            spark (SparkSession): current spark session object

        Raises:
            MinimalETLException

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

        if len(self.upstream_tasks) != 1:
            self.status = TaskStatus.FAILED
            logger.error(
                "Task type - %s must have only 1 upstream task configured",
                self.task_type,
            )
            raise MinimalETLException(
                f"Task type - {self.task_type} must have only 1 upstream task configured"
            )

        match self.config["_type"]:
            case "rdbms":
                await SparkSinkWriter(self, spark).db_writer()

            case "local_file":
                await SparkSinkWriter(self, spark).local_file_writer()

            case "gcp_bucket":
                await SparkSinkWriter(self, spark).gs_file_writer()

            case "bigquery":
                await SparkSinkWriter(self, spark).bigquery_writer()

            case _:
                self.status = TaskStatus.FAILED
                logger.error("Sink type - %s not supported", self.config["_type"])
                raise MinimalETLException(
                    f'Sink type - {self.config["_type"]} not supported'
                )

        self.status = TaskStatus.EXECUTED
        await self.pipeline.update_node_reactflow_props(
            self.uuid, "type", "successNode"
        )
        return {"task": await self.base_dict_obj()}

    async def get_schema(self) -> list[dict]:
        """method to fetch the column list for the task"""
        return [{}]
