import json
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
        if not self.config:
            self.config = {"area": None, "properties": {}}
        self.upstream_tasks = [] if self.upstream_tasks is None else self.upstream_tasks
        self.downstream_tasks = (
            [] if self.downstream_tasks is None else self.downstream_tasks
        )

    def is_configured(self) -> bool:
        """method to check if task is configured

        Returns:
            bool: True/False
        """
        if (
            self.config
            and self.config["area"] is not None
            and self.config["properties"] is not None
        ):
            return True
        return False

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

    async def validate_configurations(self, sink_config: dict):
        """method to configure task loader

        Args:
            sink_type (str): type of the sink
            sink_config (Dict): properties of the sink

        """

        try:
            sink = SinkType(sink_config.pop("source_target_area"))
            match sink:
                case "warehouse":
                    logger.info(sink_config)
                    _config = DBConfig.model_validate(sink_config)
                    _config = _config.model_dump()
                    if _config.get("extras", None) is not None:
                        _config["extras"] = json.loads(_config["extras"])
                    logger.debug(_config)
                    self.config["area"] = sink
                    self.config["properties"] = _config

                case "local_file":
                    _config = FileConfig.model_validate(sink_config)
                    _config = _config.model_dump()
                    if _config.get("extras", None) is not None and _config.get(
                        "extras"
                    ):
                        _config["extras"] = json.loads(_config["extras"])
                    logger.debug(_config)
                    self.config["area"] = sink
                    self.config["properties"] = _config

                case "gcp_bucket":
                    _config = GSFileConfig.model_validate(sink_config)
                    logger.debug(_config)
                    self.config["area"] = sink
                    self.config["properties"] = _config.model_dump()

                case "bigquery":
                    _config = BigQueryConfig.model_validate(sink_config)
                    self.config["area"] = sink
                    self.config["properties"] = _config.model_dump()

                case _:
                    logger.error(
                        "Error while configuring task - %s | %s",
                        self.uuid,
                        sink_config["type"],
                    )
                    raise MinimalETLException(
                        "Error while saving configurations. Please check the details."
                    )
            self.status = TaskStatus.CONFIGURED
        except Exception as excep:
            logger.error("Error - %s", excep.args)
            raise MinimalETLException(f"Error - {excep.args}")

    async def execute(self, spark: SparkSession) -> dict:
        """method to execute task

        Args:
            spark (SparkSession): current spark session object

        Raises:
            MinimalETLException

        """
        try:
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

            await SparkSinkWriter(current_task=self, spark=spark).write()

            self.status = TaskStatus.EXECUTED
            await self.pipeline.update_node_reactflow_props(
                self.uuid, "type", "successNode"
            )
            return await self.base_dict_obj()
        except Exception as excep:
            self.pipeline.tasks[self.uuid]["status"] = "failed"
            await self.pipeline.save()
            await self.pipeline.update_node_reactflow_props(
                self.uuid, "type", "failNode"
            )
            raise MinimalETLException(
                f"Failed to execute task - {self.name} | {excep.args}"
            )

    async def get_schema(self) -> dict:
        """method to fetch the column list for the task"""
        return {}
