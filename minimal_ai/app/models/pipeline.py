import asyncio
import json
import logging
import math
import os
import random
import shutil
from datetime import datetime
from queue import Queue
from typing import Any, Dict, List

import aiofiles
from pydantic.dataclasses import dataclass
from pydantic.fields import Field

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.entity import PipelineExecutionEntity, PipelineSchedulerEntity
from minimal_ai.app.models._task import (
    DataLoaderTask,
    DataSinkTask,
    DataTransformerTask,
)
from minimal_ai.app.models.variable import VariableManager
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.spark_main import SparkMain
from minimal_ai.app.utils.constants import (
    ICONSET,
    ExecutorType,
    PipelineStatus,
    PipelineUpdateModel,
)
from minimal_ai.app.utils.string_utils import clean_name, format_enum

METADATA_FILE = "metadata.json"
VARIABLE_DIR = ".variable"
task_type = {
    "data_loader": DataLoaderTask,
    "data_transformer": DataTransformerTask,
    "data_sink": DataSinkTask,
}

logger = logging.getLogger(__name__)


@dataclass
class Pipeline:
    uuid: str
    name: str | None = None
    description: str | None = None
    tasks: Dict[Any, Any] = Field(default={})
    executor_config: Dict[Any, Any] = Field(default={})
    executor_type: ExecutorType = ExecutorType.PYTHON
    config: Dict | None = None
    scheduled: bool = False
    status: PipelineStatus = PipelineStatus.DRAFT
    reactflow_props: Dict[Any, Any] = Field(default={})
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    modified_at: str | None = None
    created_by: str = "test user"
    modified_by: str | None = None

    def __post_init__(self):
        """
        method to run post object creation
        Returns: None

        """
        self.config = (
            self.load_config_file()
            if self.config is None
            else self.load_config(self.config)
        )

    @property
    def config_dir(self):
        """
        path to config file for the pipeline
        """
        return os.path.join(
            settings.MINIMAL_AI_REPO_PATH, settings.PIPELINES_DIR, self.uuid
        )

    @property
    def variable_dir(self):
        """
        path to variable dir
        """
        return os.path.join(self.config_dir, VARIABLE_DIR)

    @property
    def variable_manager(self):
        """
        variable manager for the pipeline
        """
        return VariableManager.get_manager(self.variable_dir)

    def load_config_file(self) -> None:
        """
        method to load configurations from config pipeline
        Returns: Dict

        """
        logger.info("Reading config file for pipeline %s", self.uuid)
        if not os.path.exists(self.config_dir):
            logger.error("Pipeline %s doesn't exists", self.uuid)
            raise MinimalETLException(f"Pipeline - {self.uuid} doesn't exists")

        with open(os.path.join(self.config_dir, METADATA_FILE)) as _file:
            _config = json.load(_file)

        self.load_config(_config)

    def load_config(self, _config: Dict) -> None:
        """
        method to load json metadata file
        Returns:

        """
        self.name = _config.get("name")
        self.uuid = _config.get("uuid")  # type: ignore
        self.description = _config.get("description")
        self.executor_type = _config.get("executor_type", "python")
        self.executor_config = _config.get("executor_config", {})
        self.tasks = _config.get("tasks", {})
        self.status = PipelineStatus(_config.get("status"))
        self.scheduled = _config.get("scheduled", False)
        self.created_at = _config.get(
            "created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.created_by = _config.get("created_by", "test user")
        self.modified_at = _config.get("modified_at")
        self.modified_by = _config.get("modified_by")
        self.reactflow_props = _config.get("reactflow_props", {})

    def base_obj(self) -> Dict:
        """
        method to get the Pipeline object dictionary
        Returns: Dict -> pipeline

        """
        return {
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description,
            "executor_type": self.executor_type,
            "executor_config": self.executor_config,
            "tasks": self.tasks,
            "status": self.status,
            "scheduled": self.scheduled,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "modified_at": self.modified_at,
            "modified_by": self.modified_by,
            "reactflow_props": self.reactflow_props,
        }

    async def pipeline_summary(self) -> Dict:
        base_data = self.base_obj()
        base_data.update(
            {
                "next_run_time": await self.next_run_time(),
                "execution_summary": await self.execution_summary_by_uuid(),
            }
        )
        return base_data

    @classmethod
    def create(
        cls,
        name: str,
        executor_type: str = ExecutorType.PYTHON,
        executor_config: Dict[str, str] | None = None,
        description: str | None = None,
    ) -> "Pipeline":
        """
        method to create object pipeline class
        Args:
            name (str): name of the pipeline
            executor_type(str): executor type of the pipeline
            executor_config (Dict): spark config of the pipeline
            description (str): short description for the pipeline
        """
        logger.info("creating pipeline %s", name)
        uuid = clean_name(name)
        pipeline_path = os.path.join(
            settings.MINIMAL_AI_REPO_PATH, settings.PIPELINES_DIR, uuid
        )
        variable_path = os.path.join(pipeline_path, VARIABLE_DIR)

        if os.path.exists(pipeline_path):
            logger.error("Pipeline %s already exists.", name)
            raise MinimalETLException(f"Pipeline - {name} already exists.")
        os.makedirs(pipeline_path)
        os.makedirs(variable_path)

        logger.debug("pipeline dir -> %s", pipeline_path)
        logger.debug("variable dir -> %s", variable_path)
        try:
            with open(os.path.join(pipeline_path, METADATA_FILE), "w") as config_file:
                json.dump(
                    {
                        "name": name,
                        "uuid": uuid,
                        "description": description,
                        "tasks": {},
                        "executor_type": ExecutorType(executor_type),
                        "executor_config": executor_config if executor_config else {},
                        "status": format_enum(PipelineStatus.DRAFT),
                        "scheduled": False,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "created_by": "test user",
                        "reactflow_props": {
                            "nodes": [],
                            "edges": [],
                            "viewport": {"x": 500, "y": 50, "zoom": 1},
                        },
                    },
                    config_file,
                    indent=4,
                )
        except Exception as excep:
            shutil.rmtree(pipeline_path)
            logger.error(
                "Failed to save metadata.json for pipeline - %s | %s", name, excep.args
            )
            raise MinimalETLException(
                f"Failed to save metadata.json for pipeline - {name} | {excep.args}"
            )

        pipeline = Pipeline(uuid=uuid)

        return pipeline

    @classmethod
    async def get_pipeline_async(cls, uuid: str) -> "Pipeline":
        """method to get pipeline object from uuid

        Args:
            uuid (str): uuid of pipeline

        Returns:
            Pipeline
        """

        config_path = os.path.join(
            settings.MINIMAL_AI_REPO_PATH,
            settings.PIPELINES_DIR,
            uuid,
            METADATA_FILE,
        )

        if not os.path.exists(config_path):
            logger.error("Pipeline %s does not exist.", uuid)
            raise MinimalETLException(f"Pipeline - {uuid} does not exist.")
        async with aiofiles.open(config_path, mode="r") as config_file:
            try:
                logger.info("Loading Pipeline %s", uuid)
                config = json.loads(await config_file.read()) or {}
            except Exception as err:
                config = {}
                logger.info(err)
        pipeline = cls(uuid=uuid, config=config)

        return pipeline

    @classmethod
    def get_pipeline(cls, uuid: str) -> "Pipeline":
        """method to get pipeline object from uuid

        Args:
            uuid (str): uuid of pipeline

        Returns:
            Pipeline
        """

        config_path = os.path.join(
            settings.MINIMAL_AI_REPO_PATH,
            settings.PIPELINES_DIR,
            uuid,
            METADATA_FILE,
        )

        if not os.path.exists(config_path):
            logger.error("Pipeline %s does not exist.", uuid)
            raise MinimalETLException(f"Pipeline - {uuid} does not exist.")
        with open(config_path, "r") as config_file:
            try:
                logger.info("Loading Pipeline %s", uuid)
                config = json.load(config_file) or {}
            except Exception as err:
                config = {}
                logger.info(err)

        pipeline = cls(uuid=uuid, config=config)

        return pipeline

    @classmethod
    def get_all_pipelines(cls) -> List:
        """method to fetch all the pipelines from the repo

        Returns:
            List[pipeline]
        """
        logger.info("Fetching pipelines from the repo")
        if not os.path.exists(settings.PIPELINES_DIR):
            os.mkdir(settings.PIPELINES_DIR)
        return [
            d
            for d in os.listdir(settings.PIPELINES_DIR)
            if cls.is_valid_pipeline(os.path.join(settings.PIPELINES_DIR, d))
        ]

    @classmethod
    def is_valid_pipeline(cls, pipeline_path) -> bool:
        """method to check id the pipeline is valid or not

        Args:
            pipeline_path (str): path to pipeline dir

        Returns:
            bool
        """
        return os.path.isdir(pipeline_path) and os.path.exists(
            os.path.join(pipeline_path, METADATA_FILE)
        )

    @classmethod
    async def summary(cls) -> Dict[str, int]:
        """method to fetch execution summary of pipelines

        Args:
            db (Asyncsession): database session

        Returns:
            Dict: summary of pipelines execution
        """
        logger.info("Fetching execution summary for the pipelines")
        summary = {}
        summary["total_pipelines"] = len(cls.get_all_pipelines())
        summary[
            "execution_details"
        ] = await PipelineExecutionEntity().get_execution_summary()

        return summary

    async def next_run_time(self) -> str | None:
        """
        next run time of the pipeline
        """
        logger.info("Fetching next run time for pipeline - %s", self.uuid)

        return (await PipelineSchedulerEntity().get(self.uuid))["next_run_time"]

    async def execution_summary_by_uuid(self) -> dict | None:
        """method to get the pipeline execution summary"""
        logger.info("fetching pipeline execution summary for pipeline - %s", self.uuid)
        summary = await PipelineExecutionEntity().get_execution_summary(self.uuid)
        if summary:
            return summary
        return None

    def delete(self):
        """method to delete the pipeline"""
        logger.info("Deleting Pipeline - %s", self.uuid)
        shutil.rmtree(self.config_dir)

    def has_task(self, task_uuid: str) -> bool:
        """method to check if task exists in pipeline

        Args:
            task_uuid (str): uuid of the task
        """

        return task_uuid in self.tasks

    async def add_edge_reactflow_props(self, target: str, source: str) -> None:
        """method to add edge to reactflow props of pipeline

        Args:
            target (str): name of target task
            source (str): name of source task
        """
        logger.info("Adding edge and updating task dependency")

        EDGE = {
            "animated": True,
            "markerEnd": {"type": "arrowclosed"},
            "source": "",
            "sourceHandle": None,
            "target": "",
            "targetHandle": None,
            "id": "reactflow__edge-source-target",
        }

        EDGE["source"] = source
        EDGE["target"] = target
        EDGE["id"] = f"reactflow__edge-{source}-{target}"

        self.reactflow_props["edges"].append(EDGE)

    async def remove_edge_reactflow_props(self, target: str) -> None:
        """method to remove edge from reactflow props of pipeline

        Args:
            target (str): uuid of task
        """
        logger.info("Removing edge from reactflow props of pipeline - %s", self.uuid)
        edges: list = []
        if self.reactflow_props["edges"]:
            for edge in self.reactflow_props["edges"]:
                if edge["target"] != target:
                    edges.append(edge)
        self.reactflow_props["edges"] = edges

    async def add_node_reactflow_props(self, task) -> None:
        """method to add node to reactflow props of pipeline object

        Args:
            task
        """
        logger.info("Adding node to reactflow props of pipeline - %s", self.uuid)

        NODE = {
            "width": 124,
            "height": 70,
            "id": "",
            "sourcePosition": "right",
            "targetPosition": "left",
            "data": {"title": "", "icon": "", "type": ""},
            "type": "draftNode",
            "position": {
                "x": math.floor(random.random() * 100),
                "y": math.floor(random.random() * 100),
            },
            "positionAbsolute": {
                "x": math.floor(random.random() * 100),
                "y": math.floor(random.random() * 100),
            },
        }

        NODE["id"] = task.uuid
        NODE["data"]["title"] = task.name
        NODE["data"]["icon"] = ICONSET[task.task_type]
        NODE["data"]["type"] = task.task_type

        self.reactflow_props["nodes"].append(NODE)

    async def update_node_reactflow_props(
        self, task_id: str, key: str, value: str
    ) -> None:
        """update node property for a task

        Args:
            task_id (str): id of the task
            key (str): property to be updated
            value (str): new value
        """
        logger.info("Updating node property for - %s", task_id)
        if not self.reactflow_props["nodes"]:
            logger.error("Reactflow prop empty")
            raise MinimalETLException("Reactflow prop is empty")

        for idx, node in enumerate(self.reactflow_props["nodes"]):
            if node["id"] == task_id:
                node[key] = value
                self.reactflow_props["nodes"][idx] = node

    async def remove_node_reactflow_props(self, task_uuid) -> None:
        """method to remove node from reactflow props of pipeline

        Args:
            task_uuid (str): uuid of task
        """
        logger.info("Removing node from reactflow props of pipeline - %s", self.uuid)
        if self.reactflow_props["nodes"]:
            for idx, node in enumerate(self.reactflow_props["nodes"]):
                if node["id"] == task_uuid:
                    del self.reactflow_props["nodes"][idx]

    async def add_task(self, task, priority=None) -> None:
        """method to attach task to pipeline

        Args:
            task (str): uuid of task
            priority (int): priority of task in pipeline

        """

        if priority is None or priority > len(self.tasks.keys()):
            self.tasks[task.uuid] = await task.base_dict_obj()
        else:
            task_list = list(self.tasks.items())
            task_list.insert(priority - 1, (task.uuid, await task.base_dict_obj()))
            self.tasks = dict(task_list)

        await self.add_node_reactflow_props(task)
        logger.info("Added task - %s to the pipeline", task.uuid)
        # self.validate('A cycle was formed while adding a task')

        self.save()

    def save(self) -> None:
        """method to save current pipeline"""
        self.modified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pipeline_dict = self.base_obj()
        try:
            with open(os.path.join(self.config_dir, METADATA_FILE), "w") as file_config:
                json.dump(pipeline_dict, file_config, indent=4)

            logger.info("Pipeline - %s saved successfully", self.uuid)
        except Exception as excep:
            raise MinimalETLException(
                f"Pipeline - {self.uuid} failed to save | {excep.args}"
            )

    async def update(self, pipeline_config: PipelineUpdateModel) -> None:
        """method to update the pipeline

        Args:
            pipeline_config (PipelineUpdateModel): properties to be updated

        Returns:
            Dict[Any,Any]: updated pipeline object
        """
        try:
            logger.info("Updating pipeline - %s", self.name)
            if pipeline_config.executor_config is not None:
                self.executor_config.clear()
                self.executor_config.update(pipeline_config.executor_config)

            if pipeline_config.executor_type is not None:
                self.executor_type = ExecutorType(pipeline_config.executor_type)

            if pipeline_config.reactflow_props is not None:
                self.reactflow_props.clear()
                self.reactflow_props.update(pipeline_config.reactflow_props)

            self.save()

        except Exception as excep:
            logger.error("Failed to update Pipeline - %s | %s", self.name, excep.args)
            raise MinimalETLException(
                f"Failed to update Pipeline - {self.name} | {excep.args}"
            )

    async def execute(self, root_tasks: List) -> dict:
        """method to execute the pipeline"""
        try:

            def create_task(task_conf: Dict):
                async def build_and_execute():
                    task = task_type[task_conf["task_type"]](**_task)

                    exec_data = await task.execute(spark)
                    self.tasks[task_conf["uuid"]] = exec_data["task"]

                return asyncio.create_task(build_and_execute())

            _exec = PipelineExecutionEntity()
            exec_data = await _exec.create(
                {
                    "trigger": "MANUAL",
                    "pipeline_uuid": self.uuid,
                    "execution_date": datetime.now(),
                    "status": "RUNNING",
                }
            )

            if not root_tasks:
                raise MinimalETLException(
                    f"Execution failed for pipeline {self.uuid} - no tasks have been configured"
                )

            spark, _ = SparkMain(self.uuid, self.executor_config).start_spark()
            task_queue = Queue()
            executed_tasks = {}
            for _task in root_tasks:
                task_queue.put(_task)
                executed_tasks[_task] = None

            while not task_queue.empty():
                task_uuid = task_queue.get()
                task_conf = self.tasks[task_uuid]

                skip = False
                for upstream_task in task_conf["upstream_tasks"]:
                    if executed_tasks.get(upstream_task) is None:
                        task_queue.put(task_uuid)
                        skip = True
                        break
                if skip:
                    continue

                upstream_tasks = [
                    executed_tasks[uuid] for uuid in task_conf["upstream_tasks"]
                ]
                await asyncio.gather(*upstream_tasks)

                task_stat = create_task(task_conf)
                executed_tasks[task_uuid] = task_stat
                for downstream_task in task_conf["downstream_tasks"]:
                    if downstream_task not in executed_tasks:
                        executed_tasks[downstream_task] = None
                        task_queue.put(downstream_task)
            remaining_tasks = filter(
                lambda task: task is not None, executed_tasks.values()
            )
            await asyncio.gather(*remaining_tasks)
            spark.stop()
            self.status = PipelineStatus.EXECUTED
            self.save()

            await PipelineExecutionEntity().update(
                key="id", value=exec_data["id"], payload={"status": "COMPLETED"}
            )
            return await self.pipeline_summary()
        except Exception as excep:
            self.status = PipelineStatus.FAILED
            self.save()
            logger.error(
                "Error while executing pipeline - %s | %s", self.uuid, excep.args
            )
            await PipelineExecutionEntity().update(
                key="id",
                value=exec_data["id"],  # type: ignore
                payload={"status": "FAILED"},
            )

            return await self.pipeline_summary()

    async def scheduled_execute(self, root_tasks: List) -> None:
        """method to execute the pipeline at scheduled time"""
        try:

            def create_task(task_conf: Dict):
                async def build_and_execute():
                    task = task_type[task_conf["task_type"]](**_task)
                    exec_data = await task.execute(spark)
                    self.tasks[task_conf["uuid"]] = exec_data["task"]

                return asyncio.create_task(build_and_execute())

            _exec = PipelineExecutionEntity()
            exec_data = await _exec.create(
                {
                    "trigger": "SCHEDULED",
                    "pipeline_uuid": self.uuid,
                    "execution_date": datetime.now(),
                    "status": "RUNNING",
                }
            )

            spark, _ = SparkMain(self.uuid, self.executor_config).start_spark()
            task_queue = Queue()
            executed_tasks = {}
            for _task in root_tasks:
                task_queue.put(_task)
                executed_tasks[_task] = None

            while not task_queue.empty():
                task_uuid = task_queue.get()
                task_conf = self.tasks[task_uuid]

                skip = False
                for upstream_task in task_conf["upstream_tasks"]:
                    if executed_tasks.get(upstream_task) is None:
                        task_queue.put(task_uuid)
                        skip = True
                        break
                if skip:
                    continue

                upstream_tasks = [
                    executed_tasks[uuid] for uuid in task_conf["upstream_tasks"]
                ]
                await asyncio.gather(*upstream_tasks)

                task_stat = create_task(task_conf)
                executed_tasks[task_uuid] = task_stat
                for downstream_task in task_conf["downstream_tasks"]:
                    if downstream_task not in executed_tasks:
                        executed_tasks[downstream_task] = None
                        task_queue.put(downstream_task)
            remaining_tasks = filter(
                lambda task: task is not None, executed_tasks.values()
            )
            await asyncio.gather(*remaining_tasks)
            spark.stop()
            self.status = PipelineStatus.EXECUTED
            self.save()
            await PipelineExecutionEntity().update(
                key="id", value=exec_data["id"], payload={"status": "COMPLETED"}
            )

        except Exception as excep:
            self.status = PipelineStatus.FAILED
            self.save()
            await PipelineExecutionEntity().update(
                key="id",
                value=exec_data["id"],  # type: ignore
                payload={"status": "FAILED"},
            )

            raise MinimalETLException(
                f"Pipeline - {self.uuid} failed to execute | {excep.args}"
            )
