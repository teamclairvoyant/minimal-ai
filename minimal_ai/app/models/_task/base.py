import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass
class _Task(ABC):
    uuid: str
    name: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.DRAFT
    pipeline: Any = None
    config: dict = Field(default_factory=dict)
    upstream_tasks: list[str] = Field(default_factory=list)
    downstream_tasks: list[str] = Field(default_factory=list)

    @property
    def all_upstream_task_executed(self):
        """
        Task property to check if all upstream task is executed
        """
        _executed = True
        for task_uuid in self.upstream_tasks:
            _task = self.pipeline.tasks[task_uuid]
            if _task["status"] != "executed":
                _executed = False
                break
        return _executed

    @property
    def is_configured(self) -> bool:
        """method to check if task is configured

        Returns:
            bool: True/False
        """
        if (
            self.config
            and (self.config and self.config["_type"] is not None)
            and (self.config and self.config["properties"] is not None)
        ):
            return True
        return False

    @property
    async def records(self) -> list:
        """sample records from the task"""
        if self.status == "executed":
            return await self.pipeline.variable_manager.get_variable_data(self.uuid)
        raise MinimalETLException(
            "Sample records not loaded. Execute the task to load the data"
        )

    @classmethod
    @abstractmethod
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

    async def after_create(self, **kwargs) -> None:
        """method to add task to corresponding pipeline"""
        if kwargs.get("upstream_task_uuids") is not None:
            self.upstream_tasks.extend(
                kwargs.get("upstream_task_uuids")  # type: ignore
            )
        await self.update_upstream_tasks(
            add_to_task_uuids=kwargs.get("upstream_task_uuids")
        )
        pipeline = kwargs.get("pipeline")
        if pipeline is not None:
            priority = kwargs.get("priority")

            await pipeline.add_task(
                self,
                priority=priority,
            )

    async def update_upstream_tasks(
        self, add_to_task_uuids=None, remove_from_task_uuids=None
    ) -> None:
        """method to update the upstream tasks of current task

        Args:
            add_to_task_uuids (list, optional): upstream tasks to update. Defaults to [].
            remove_from_task_uuids (list, optional): upstream tasks to update. Defaults to [].

        Raises:
            MinimalETLException: upstream task not defined in pipeline
        """

        if add_to_task_uuids is None:
            add_to_task_uuids = []
        if remove_from_task_uuids is None:
            remove_from_task_uuids = []
        if add_to_task_uuids:
            logger.debug(add_to_task_uuids)
            for task_uuid in add_to_task_uuids:
                if not self.pipeline.has_task(task_uuid):
                    logger.error(
                        "Task - %s not defined in pipeline - %s",
                        task_uuid,
                        self.pipeline.uuid,
                    )
                    raise MinimalETLException(
                        f"Task - {task_uuid} not defined in pipeline - {self.pipeline.uuid}"
                    )
                self.pipeline.tasks[task_uuid]["downstream_tasks"].append(self.uuid)
                await self.pipeline.add_edge_reactflow_props(self.uuid, task_uuid)

        if remove_from_task_uuids:
            logger.debug(remove_from_task_uuids)
            for task_uuid in remove_from_task_uuids:
                if not self.pipeline.has_task(task_uuid):
                    logger.error(
                        "Task - %s not defined in pipeline - %s",
                        task_uuid,
                        self.pipeline.uuid,
                    )
                    raise MinimalETLException(
                        f"Task - {task_uuid} not defined in pipeline - {self.pipeline.uuid}"
                    )
                self.pipeline.tasks[task_uuid]["downstream_tasks"].remove(self.uuid)

    async def base_dict_obj(self) -> dict:
        """method to get task dict object"""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "status": self.status,
            "task_type": self.task_type,
            "configured": self.is_configured,
            "config": self.config,
            "upstream_tasks": self.upstream_tasks,
            "downstream_tasks": self.downstream_tasks,
        }
