import json
import logging
import os

import aiofiles
from pydantic.dataclasses import dataclass
from pyspark.sql import SparkSession

from minimal_ai.app.models._task.base import _Task
from minimal_ai.app.pipeline_templates.utils import fetch_template
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.transformer.source_reader import SparkSourceReaders
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass
class DataLoaderTask(_Task):
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

        task = DataLoaderTask(
            uuid=uuid, name=name, task_type=TaskType(task_type), pipeline=pipeline
        )

        await task.after_create(
            pipeline=pipeline,
            priority=priority,
            upstream_task_uuids=upstream_task_uuids,
        )

    async def get_schema(self) -> dict:
        """method to fetch the column list for the task"""
        try:
            logger.info("fetching schema from source - %s", self.config["area"])
            if self.status == "executed":
                return self.pipeline.variable_manager.get_variable_data(self.uuid)[
                    "columns"
                ]

            raise MinimalETLException("unable to fetch schema")
        except Exception as excep:
            logger.error("error while fetching schema - %s", excep.args)
            raise MinimalETLException(excep.args)

    async def generate_code_from_template(self) -> None:
        """method to generate loader code from template"""
        try:
            logger.info("Generating code template")
            options = ""
            rendered_code = ""
            if self.config["properties"]["extras"]:
                options = ", ".join(
                    [
                        f'{prop}="{value}"'
                        for prop, value in self.config["properties"]["extras"].items()
                    ]
                )

            match self.config["properties"]["type"]:
                case "csv":
                    code_template = fetch_template("tasks/data_loader/csv_reader.jinja")
                    rendered_code = code_template.render(
                        task_uuid=self.uuid,
                        options=options,
                        file_path=self.config["properties"]["file_path"],
                    )
                case "json":
                    code_template = fetch_template(
                        "tasks/data_loader/json_reader.jinja"
                    )
                    rendered_code = code_template.render(
                        task_uuid=self.uuid,
                        options=options,
                        file_path=self.config["properties"]["file_path"],
                    )
                case "parquet":
                    code_template = fetch_template(
                        "tasks/data_loader/parquet_reader.jinja"
                    )
                    rendered_code = code_template.render(
                        task_uuid=self.uuid,
                        options=options,
                        file_path=self.config["properties"]["file_path"],
                    )
                case "mysql":
                    code_template = fetch_template(
                        "tasks/data_loader/mysql_reader.jinja"
                    )
                    rendered_code = code_template.render(
                        task_uuid=self.uuid,
                        options=options,
                        host=self.config["properties"]["host"],
                        port=self.config["properties"]["port"],
                        database=self.config["properties"]["database"],
                        table=self.config["properties"]["table"],
                        user=self.config["properties"]["user"],
                        password=self.config["properties"]["password"],
                    )
                case _:
                    logger.error("Not implemented yet")

            async with aiofiles.open(
                os.path.join(self.pipeline.config_dir, "Tasks", f"{self.uuid}.py"),
                mode="w",
            ) as py_file:
                await py_file.write(rendered_code)

        except Exception as excep:
            logger.error(excep.args)

    async def validate_configurations(self, loader_config: dict):
        """method to configure task loader

        Args:
            loader_config (Dict): properties of the loader

        """
        try:
            loader = LoaderType(loader_config.pop("source_target_area"))

            match loader:
                case "warehouse":
                    _config = DBConfig.model_validate(loader_config)
                    _config = _config.model_dump()
                    if _config.get("extras", None) is not None and _config.get(
                        "extras"
                    ):
                        _config["extras"] = json.loads(_config["extras"])
                    logger.debug(_config)
                    self.config["area"] = loader
                    self.config["properties"] = _config

                case "local_file":
                    _config = FileConfig.model_validate(loader_config)
                    _config = _config.model_dump()
                    if _config.get("extras", None) is not None and _config.get(
                        "extras"
                    ):
                        _config["extras"] = json.loads(_config["extras"])
                    logger.debug(_config)
                    self.config["area"] = loader
                    self.config["properties"] = _config

                case "gcp_bucket":
                    _config = GSFileConfig.model_validate(loader_config)
                    logger.debug(_config)
                    self.config["area"] = loader
                    self.config["properties"] = _config.model_dump()

                case "bigquery":
                    _config = BigQueryConfig.model_validate(loader_config)
                    self.config["area"] = loader
                    self.config["properties"] = _config.model_dump()

                case _:
                    logger.error(
                        "Error while configuring task - %s | %s",
                        self.uuid,
                        loader_config["type"],
                    )
                    raise MinimalETLException(
                        "Error while saving configurations. Please check the details."
                    )
            await self.generate_code_from_template()
            self.status = TaskStatus.CONFIGURED
        except Exception as excep:
            logger.error("Error - %s", excep.args)
            raise MinimalETLException(f"Error - {excep.args}")

    async def execute(self, spark: SparkSession, standalone: bool = False) -> dict:
        """
        async method to execute the task
        Args:
            spark (SparkSession): current spark session object

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

            await SparkSourceReaders(current_task=self, spark=spark).read()

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
