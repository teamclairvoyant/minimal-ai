import json
import logging
from typing import Dict

import polars as pl

from minimal_ai.app.services import PipelineService, TaskService

from .constants import PipelineModel, TaskModel

logger = logging.getLogger(__name__)


async def to_json(excel_file: str) -> None:
    """method to convert excel to json

    Args:
        excel_file (str): name of excel file

    """

    df_pipeline: pl.DataFrame = pl.read_excel(
        excel_file, sheet_name='pipeline')
    df_tasks: pl.DataFrame = pl.read_excel(excel_file, sheet_name='tasks')

    tasks_dict: Dict = json.loads(df_tasks.write_json(row_oriented=True))
    pipeline_dict: Dict = json.loads(df_pipeline.write_json(row_oriented=True))

    pipeline_model: PipelineModel = PipelineModel.parse_obj(pipeline_dict[0])

    pipeline = await PipelineService.create_pipeline(**pipeline_model.dict())

    task_update_config = {}
    # init_tasks = []
    for task_dict in tasks_dict:
        task_update_config['config_type'] = task_dict.pop('config_type')
        task_update_config['config_properties'] = json.loads(task_dict.pop(
            'config_properties'))
        logger.info(task_update_config)
        if task_dict['upstream_task_uuids'] is not None:
            task_dict['upstream_task_uuids'] = task_dict['upstream_task_uuids'].split(
                ',')
        task_model: TaskModel = TaskModel.parse_obj(task_dict)
        task = await TaskService.add_task_to_pipeline(
            pipeline['uuid'], task_model)
        await TaskService.update_task_by_excel(
            pipeline['uuid'], task['uuid'], task_update_config)

    # await asyncio.gather(*init_tasks)
    # for task in init_tasks:
    #     await task

    logger.info(pipeline)
