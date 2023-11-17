import logging

from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.models._task.base import _Task
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.transformer.spark_transformers import SparkTransformer
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass
class DataTransformerTask(_Task):
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

        task = DataTransformerTask(
            uuid=uuid, name=name, task_type=TaskType(task_type), pipeline=pipeline
        )

        await task.after_create(
            pipeline=pipeline,
            priority=priority,
            upstream_task_uuids=upstream_task_uuids,
        )

    async def validate_configurations(
        self, transformer_type: str, transformer_config: dict
    ):
        """method to configure task loader

        Args:
            transformer_type (str): type of the sink
            transformer_config (Dict): properties of the sink

        """
        try:
            transformer = TransformerType(transformer_type)
            logger.info(transformer)

            match transformer:
                case "sparkAI":
                    _config = FilterModel.model_validate(transformer_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer_type,
                        self.uuid,
                    )
                    self.config["_type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case "join":
                    _config = JoinModel.model_validate(transformer_config)
                    logger.debug(_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer_type,
                        self.uuid,
                    )
                    self.config["_type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case "filter":
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer_type,
                        self.uuid,
                    )
                    _config = FilterModel.model_validate(transformer_config)
                    self.config["_type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case "pivot":
                    _config = PivotModel.model_validate(transformer_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer_type,
                        self.uuid,
                    )
                    self.config["_type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case _:
                    logger.error(
                        "Transformer type - %s not supported", transformer_type
                    )
                    raise MinimalETLException(
                        f"Transformer type - {transformer_type} not supported"
                    )
        except Exception as excep:
            logger.error(
                "Transformer type - %s not supported | %s", transformer_type, excep.args
            )
            raise MinimalETLException(
                f"Transformer type - {transformer_type} not supported | {excep.args}"
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

        await SparkTransformer(current_task=self, spark=spark).transform()

        self.status = TaskStatus.EXECUTED
        await self.pipeline.update_node_reactflow_props(
            self.uuid, "type", "successNode"
        )
        return {"task": await self.base_dict_obj()}

    async def get_schema(self) -> list[dict]:
        """method to fetch the column list for the task"""
        return [{}]
