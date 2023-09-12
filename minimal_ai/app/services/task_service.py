import json
import logging
import os
from typing import Dict

import aiofiles
from fastapi import Request, UploadFile

from minimal_ai.app.models.pipeline import Pipeline
from minimal_ai.app.models.task import Task
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils import TaskModel, TaskUpdateModel

logger = logging.getLogger(__name__)


class TaskService:

    @staticmethod
    async def add_task_to_pipeline(pipeline_uuid: str, task_config: TaskModel) -> Dict:
        """ method to add task to a pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_config (TaskModel): configuration of the task to be created
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Pipeline - %s', pipeline.uuid)
        Task.create(task_config.name,
                    task_config.task_type,
                    pipeline=pipeline,
                    priority=task_config.priority,
                    upstream_task_uuids=task_config.upstream_task_uuids)

        return pipeline.base_obj()

    @staticmethod
    async def get_task(pipeline_uuid: str, task_uuid: str) -> Dict:
        """ method to get task from pipeline

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task

        Returns:
            Dict: task object
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Pipeline - %s', pipeline.uuid)

        if not pipeline.has_task(task_uuid):
            logger.error('Task - %s not defined in pipeline - %s',
                         task_uuid, pipeline_uuid)
            raise MinimalETLException(
                f'Task - {task_uuid} not defined in pipeline - {pipeline_uuid}')

        return pipeline.tasks[task_uuid]

    @staticmethod
    async def get_sample_records(pipeline_uuid: str, task_uuid: str) -> Dict:
        """method to fetch sample records from executed task

        Args:
            pipeline_uuid (str): uuid of pipeline
            task_uuid (str): uuid of task
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Pipeline - %s', pipeline.uuid)
        if not pipeline.has_task(task_uuid):
            logger.error('Task - %s not defined in pipeline - %s',
                         task_uuid, pipeline_uuid)
            raise MinimalETLException(
                f'Task - {task_uuid} not defined in pipeline - {pipeline_uuid}')
        task = Task.get_task_from_config(pipeline.tasks[task_uuid], pipeline)

        data = await task.records

        return {'columns': [{'field': key} for key in data[0].keys()],
                'records': data}

    @staticmethod
    async def get_all_tasks(pipeline_uuid: str) -> Dict:
        """ method to fetch all the tasks from the pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline

        Returns:
            Dict: task object
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Pipeline - %s', pipeline.uuid)

        return pipeline.tasks

    @staticmethod
    async def delete_task(pipeline_uuid: str, task_uuid: str) -> Dict:
        """ method to delete task from the pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_uuid (str): uuid of the task
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Pipeline - %s', pipeline_uuid)

        if not pipeline.has_task(task_uuid):
            logger.error('Task - %s not defined in Pipeline - %s.',
                         task_uuid, pipeline_uuid)
            raise MinimalETLException(
                f'Task - {task_uuid} not defined in pipeline {pipeline_uuid}')

        logger.info('Found task - %s in the pipeline', task_uuid)

        if pipeline.tasks[task_uuid]['downstream_tasks']:
            logger.error(
                'Task - %s has downstream tasks. Please delete them first.', task_uuid)
            raise MinimalETLException(
                f'Task - {task_uuid} has downstream tasks. Please delete them first')

        task = pipeline.tasks.pop(task_uuid)

        if task['upstream_tasks']:
            for _task_uuid in task['upstream_tasks']:
                pipeline.tasks[_task_uuid]['downstream_tasks'].remove(
                    task_uuid)

        logger.info('Deleted Task - %s', task_uuid)
        logger.info('Saving Pipeline - %s', pipeline_uuid)

        pipeline.save()
        return task

    @staticmethod
    async def update_task_by_config(pipeline_uuid: str, task_uuid: str, request: Request) -> Dict:
        """ method to update task by config

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_uuid (str): uuid of the task
            request (TaskUpdateModel): properties of task to be updated

        Returns:
            Dict: task object
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Loading task - %s', task_uuid)
        if not pipeline.has_task(task_uuid):
            logger.error('Task - %s not defined in Pipeline - %s.',
                         task_uuid, pipeline_uuid)
            raise MinimalETLException(
                f'Task - {task_uuid} not defined in pipeline {pipeline_uuid}')

        _task = pipeline.tasks[task_uuid]

        task = Task.get_task_from_config(_task, pipeline)

        if not await request.form():
            task_config = TaskUpdateModel(**json.loads(await request.body()))
            if task_config.upstream_task_uuids is not None and task.upstream_tasks is not None:
                logger.info(
                    'Updating upstream tasks for the task - %s', task_uuid)
                if task_config.upstream_task_uuids:
                    task.upstream_tasks.extend(task_config.upstream_task_uuids)
                    task.update_upstream_tasks(task_config.upstream_task_uuids)
                else:
                    current_upstream_task_uuids = task.upstream_tasks
                    task.upstream_tasks = []
                    task.update_upstream_tasks(
                        remove_from_task_uuids=current_upstream_task_uuids)

            if task_config.config_type is not None or task_config.config_properties is not None:
                logger.info('Updating task config and properties')
                task.validate_configurations(task_config.config_type,
                                             task_config.config_properties)
        else:
            task_form = await request.form()
            data_file: UploadFile = task_form.get('data_file')  # type: ignore
            task_config = {'file_type': task_form.get('file_type'),
                           'file_name': data_file.filename}
            task.validate_configurations('file', task_config)
            async with aiofiles.open(os.path.join(task.pipeline.variable_dir, task_config.get('file_name')),  # type: ignore
                                     'wb') as file:
                await file.write(await data_file.read())

        pipeline.tasks[task_uuid] = task.base_dict_obj()
        logger.info('Updating pipeline - %s', pipeline_uuid)
        pipeline.save()
        return pipeline.base_obj()

    @staticmethod
    async def update_task_by_excel(pipeline_uuid: str, task_uuid: str, excel_config: Dict) -> Dict:
        """ method to update task by excel file

        Args:
            pipeline_uuid (str): uuid of the pipeline
            task_uuid (str): uuid of the task
            request (TaskUpdateModel): properties of task to be updated

        Returns:
            Dict: task object
        """

        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info('Loading task - %s', task_uuid)
        if not pipeline.has_task(task_uuid):
            logger.error('Task - %s not defined in Pipeline - %s.',
                         task_uuid, pipeline_uuid)
            raise MinimalETLException(
                f'Task - {task_uuid} not defined in pipeline {pipeline_uuid}')

        _task = pipeline.tasks[task_uuid]

        task = Task.get_task_from_config(_task, pipeline)

        task_config = TaskUpdateModel.parse_obj(excel_config)

        if task_config.upstream_task_uuids is not None and task.upstream_tasks is not None:
            logger.info(
                'Updating upstream tasks for the task - %s', task_uuid)
            if task_config.upstream_task_uuids:
                task.upstream_tasks.extend(task_config.upstream_task_uuids)
                task.update_upstream_tasks(task_config.upstream_task_uuids)
            else:
                current_upstream_task_uuids = task.upstream_tasks
                task.upstream_tasks = []
                task.update_upstream_tasks(
                    remove_from_task_uuids=current_upstream_task_uuids)

        if task_config.config_type is not None or task_config.config_properties is not None:
            logger.info('Updating task config and properties')
            task.validate_configurations(task_config.config_type,
                                         task_config.config_properties)

        pipeline.tasks[task_uuid] = task.base_dict_obj()
        logger.info('Updating pipeline - %s', pipeline_uuid)
        pipeline.save()
        return task.base_dict_obj()
