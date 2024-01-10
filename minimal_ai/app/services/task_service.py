import json
import logging
from typing import Dict

from fastapi import Request

from minimal_ai.app.models._task import (
    DataLoaderTask,
    DataSinkTask,
    DataTransformerTask,
)
from minimal_ai.app.models.pipeline import Pipeline
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.spark_main import SparkMain
from minimal_ai.app.utils import PipelineStatus, TaskModel, TaskUpdateModel

logger = logging.getLogger(__name__)

task_type = {
    "data_loader": DataLoaderTask,
    "data_transformer": DataTransformerTask,
    "data_sink": DataSinkTask,
}


class TaskService:
    @staticmethod
    async def add_task_to_pipeline(pipeline_uuid: str, task_config: TaskModel) -> Dict:
        """method to add task to a pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_config (TaskModel): configuration of the task to be created
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s", pipeline.uuid)

        await task_type[task_config.task_type].create(
            task_config.name,
            task_config.task_type,
            pipeline=pipeline,
            priority=task_config.priority,
            upstream_task_uuids=task_config.upstream_task_uuids,
        )

        return await pipeline.pipeline_summary()

    @staticmethod
    async def get_task(pipeline_uuid: str, task_uuid: str) -> Dict:
        """method to get task from pipeline

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task

        Returns:
            Dict: task object
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s", pipeline.uuid)

        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in pipeline - %s", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline - {pipeline_uuid}"
            )

        task_config = pipeline.tasks[task_uuid]
        task: DataLoaderTask | DataSinkTask | DataTransformerTask = task_type[
            task_config["task_type"]
        ](**task_config)
        return await task.base_dict_obj()

    @staticmethod
    async def get_schema(pipeline_uuid: str, task_uuid: str) -> dict:
        """method to get schema from task

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task

        Returns:
            Dict: task object
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s", pipeline.uuid)

        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in pipeline - %s", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline - {pipeline_uuid}"
            )
        task_config = pipeline.tasks[task_uuid]

        task: DataLoaderTask | DataSinkTask | DataTransformerTask = task_type[
            task_config["task_type"]
        ](**task_config)

        return await task.get_schema()

    @staticmethod
    async def get_sample_records(
        pipeline_uuid: str, task_uuid: str, schema: bool
    ) -> Dict:
        """method to fetch sample records from executed task

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s", pipeline.uuid)
        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in pipeline - %s", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline - {pipeline_uuid}"
            )
        task_config = pipeline.tasks[task_uuid]
        task: DataLoaderTask | DataSinkTask | DataTransformerTask = task_type[
            task_config["task_type"]
        ](**task_config)
        task.pipeline = pipeline
        variable = await task.records()

        if schema:
            return {
                "columns": variable["columns"]["fields"],
            }
        return {
            "columns": variable["columns"]["fields"],
            "records": variable["data"],
            "count": variable["count"],
        }

    @staticmethod
    async def get_all_tasks(pipeline_uuid: str) -> Dict:
        """method to fetch all the tasks from the pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline

        Returns:
            Dict: task object
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s", pipeline.uuid)

        return pipeline.tasks

    @staticmethod
    async def delete_task(pipeline_uuid: str, task_uuid: str) -> Dict:
        """method to delete task from the pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_uuid (str): uuid of the task
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s", pipeline_uuid)

        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in Pipeline - %s.", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline {pipeline_uuid}"
            )

        logger.info("Found task - %s in the pipeline", task_uuid)

        if pipeline.tasks[task_uuid]["downstream_tasks"]:
            logger.error(
                "Task - %s has downstream tasks. Please delete them first.", task_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} has downstream tasks. Please delete them first"
            )

        task = pipeline.tasks.pop(task_uuid)
        await pipeline.remove_node_reactflow_props(task["uuid"])
        await pipeline.remove_edge_reactflow_props(task["uuid"])

        if task["upstream_tasks"]:
            for _task_uuid in task["upstream_tasks"]:
                pipeline.tasks[_task_uuid]["downstream_tasks"].remove(task_uuid)

        logger.info("Deleted Task - %s", task_uuid)
        logger.info("Saving Pipeline - %s", pipeline_uuid)

        await pipeline.save()
        return await pipeline.pipeline_summary()

    @staticmethod
    async def update_task_by_config(
        pipeline_uuid: str, task_uuid: str, request: Request
    ) -> Dict:
        """method to update task by config

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_uuid (str): uuid of the task
            request (TaskUpdateModel): properties of task to be updated

        Returns:
            Dict: task object
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Loading task - %s", task_uuid)
        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in Pipeline - %s.", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline {pipeline_uuid}"
            )

        task: DataLoaderTask | DataSinkTask | DataTransformerTask = task_type[
            pipeline.tasks[task_uuid]["task_type"]
        ](**pipeline.tasks[task_uuid])
        task.pipeline = pipeline

        task_config = TaskUpdateModel(**json.loads(await request.body()))
        if (
            task_config.upstream_task_uuids is not None
            and task.upstream_tasks is not None
        ):
            logger.info("Updating upstream tasks for the task - %s", task_uuid)
            if task_config.upstream_task_uuids:
                task.upstream_tasks.extend(task_config.upstream_task_uuids)
                await task.update_upstream_tasks(task_config.upstream_task_uuids)
            else:
                current_upstream_task_uuids = task.upstream_tasks
                task.upstream_tasks = []
                await task.update_upstream_tasks(
                    remove_from_task_uuids=current_upstream_task_uuids
                )

        if task_config.config_properties is not None:
            logger.debug(task_config.config_properties)
            logger.info("Updating task config and properties")
            await task.validate_configurations(
                task_config.config_properties
            )  # type: ignore
            await pipeline.update_node_reactflow_props(
                task.uuid, "type", "configuredNode"
            )

        pipeline.tasks[task_uuid] = await task.base_dict_obj()
        pipeline.status = PipelineStatus.DRAFT
        try:
            await pipeline.variable_manager.delete_variable(task_uuid)
        except MinimalETLException:
            logger.info("No variable data found to be deleted")
        logger.info("Updating pipeline - %s", pipeline_uuid)
        await pipeline.save()
        return await pipeline.pipeline_summary()

    @staticmethod
    async def update_columns_by_task(
        pipeline_uuid: str, task_uuid: str, columns
    ) -> dict:
        """method to update column list of task

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task
            columns (list): list of cloumns
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Loading task - %s", task_uuid)
        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in Pipeline - %s.", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline {pipeline_uuid}"
            )

        _task = pipeline.tasks[task_uuid]
        task: DataLoaderTask | DataSinkTask | DataTransformerTask = task_type[
            _task["task_type"]
        ](**_task)
        if task.is_configured:
            task.config["columns"] = columns

        pipeline.tasks[task_uuid] = await task.base_dict_obj()
        logger.info("Updating pipeline - %s", pipeline_uuid)
        await pipeline.save()
        return await pipeline.pipeline_summary()

    @staticmethod
    async def execute_task_by_uuid(pipeline_uuid: str, task_uuid: str) -> dict:
        """method to execute task

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task

        Returns:
            dict: pipeline object
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Loading task - %s", task_uuid)
        if not pipeline.has_task(task_uuid):
            logger.error(
                "Task - %s not defined in Pipeline - %s.", task_uuid, pipeline_uuid
            )
            raise MinimalETLException(
                f"Task - {task_uuid} not defined in pipeline {pipeline_uuid}"
            )

        _task = pipeline.tasks[task_uuid]
        task: DataLoaderTask | DataSinkTask | DataTransformerTask = task_type[
            _task["task_type"]
        ](**_task)
        task.pipeline = pipeline

        if task.is_configured:
            spark, _ = SparkMain(pipeline.uuid, pipeline.executor_config).start_spark()
            exec_data = await task.execute(spark)
            pipeline.tasks[task_uuid] = exec_data
            spark.stop()
            await pipeline.save()
            return await pipeline.pipeline_summary()
        raise MinimalETLException(
            f"Task - {task_uuid} not configured properly. Please check the configurations before executing"
        )
