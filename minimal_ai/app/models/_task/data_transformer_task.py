import logging
import os

import aiofiles
from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.models._task.base import _Task
from minimal_ai.app.pipeline_templates.utils import fetch_template
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.transformer.spark_transformers import SparkTransformer
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass
class DataTransformerTask(_Task):
    def __post_init__(self):
        if not self.config:
            self.config = {"type": None, "properties": {}}
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
            and self.config["type"] is not None
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

        task = DataTransformerTask(
            uuid=uuid, name=name, task_type=TaskType(task_type), pipeline=pipeline
        )

        await task.after_create(
            pipeline=pipeline,
            priority=priority,
            upstream_task_uuids=upstream_task_uuids,
        )

    async def generate_code_from_template(self) -> None:
        """method to generate loader code from template"""
        try:
            logger.info("Generating code template")

            rendered_code = ""

            match self.config["type"]:
                case "join":
                    select = "*"
                    if (
                        self.config["properties"]["target_columns"]
                        or self.config["properties"]["target_columns"] is not None
                    ):
                        select = ",\n\t\t".join(
                            [
                                f'(df.{i[1]}).alias("{i[0]}")'
                                for i in self.config["properties"][
                                    "target_columns"
                                ].items()
                            ]
                        )

                    code_template = fetch_template(
                        "tasks/data_transformer/spark_join.jinja"
                    )

                    rendered_code = code_template.render(
                        task_uuid=self.uuid,
                        left_df=self.config["properties"]["left_table"],
                        right_df=self.config["properties"]["right_table"],
                        on=self.config["properties"]["on"],
                        how=self.config["properties"]["how"],
                        select_expression=select,
                        where=self.config["properties"]["where"]
                        if self.config["properties"]["where"]
                        else "",
                    )

                case "aggregate":
                    pass

                case _:
                    logger.error("Not implemented yet")

            async with aiofiles.open(
                os.path.join(self.pipeline.config_dir, "Tasks", f"{self.uuid}.py"),
                mode="w",
            ) as py_file:
                await py_file.write(rendered_code)

        except Exception as excep:
            logger.error(excep.args)

    async def validate_configurations(self, transformer_config: dict):
        """method to configure task loader

        Args:
            transformer_config (Dict): properties of the sink

        """
        try:
            transformer = TransformerType(transformer_config.pop("type"))
            logger.info(transformer)

            match transformer:
                case "join":
                    logger.debug(transformer_config)
                    _config = JoinModel.model_validate(transformer_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer.value,
                        self.uuid,
                    )
                    self.config["type"] = transformer
                    self.config["properties"] = _config.model_dump()
                    self.upstream_tasks.remove(self.config["properties"]["left_table"])
                    self.upstream_tasks.insert(
                        0, self.config["properties"]["left_table"]
                    )

                case "aggregate":
                    _config = AggModel.model_validate(transformer_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer.value,
                        self.uuid,
                    )
                    self.config["type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case "filter":
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer.value,
                        self.uuid,
                    )
                    _config = FilterModel.model_validate(transformer_config)
                    self.config["type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case "pivot":
                    _config = PivotModel.model_validate(transformer_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer.value,
                        self.uuid,
                    )
                    self.config["type"] = transformer
                    self.config["properties"] = _config.model_dump()

                case "customsql":
                    _config = CustomSql.model_validate(transformer_config)
                    logger.info(
                        "Configuring %s transformer for task - %s",
                        transformer.value,
                        self.uuid,
                    )
                    self.config["type"] = transformer
                    self.config["properties"] = _config.model_dump()
                case _:
                    logger.error(
                        "Transformer type - %s not supported", transformer.value
                    )
                    raise MinimalETLException(
                        f"Transformer type - {transformer.value} not supported"
                    )
            self.status = TaskStatus.CONFIGURED
            await self.generate_code_from_template()
        except Exception as excep:
            raise MinimalETLException(
                f"Error while configuring transformer | {excep.args}"
            )

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

            await SparkTransformer(current_task=self, spark=spark).transform()

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
