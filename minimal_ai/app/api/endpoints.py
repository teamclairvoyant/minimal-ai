import logging

import psutil
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from minimal_ai.app.entity import PipelineExecutionEntity
from minimal_ai.app.services.database import transaction
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.pipeline_service import PipelineService
from minimal_ai.app.services.task_service import TaskService
from minimal_ai.app.utils.constants import (CronModel, PipelineModel,
                                            PipelineUpdateModel, TaskModel)

api_router = APIRouter()
logger = logging.getLogger(__name__)


@api_router.get("/cpu_ram_info")
async def cpu_ram_info() -> JSONResponse:
    """endpoint to get cpu and ram info
    """
    try:
        logger.info("GET /cpu_ram_info")
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"cpu": f"{psutil.cpu_percent(interval=1)}%",
                                     "ram": f"{round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total,2)}%"})
    except Exception as excep:
        logger.error("GET /cpu_ram_info - %s", excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.get("/pipelines_summary")
async def pipelines_summary() -> JSONResponse:
    """ endpoint to fetch pipelines_summary
    """
    try:
        logger.info("GET /pipelines_summary")
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"pipelines": [
                                {
                                    "uuid": "test1",
                                    "name": "test1",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test12",
                                    "name": "test12",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test13",
                                    "name": "test13",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test14",
                                    "name": "test14",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test15",
                                    "name": "test15",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test16",
                                    "name": "test16",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test17",
                                    "name": "test17",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test18",
                                    "name": "test18",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test19",
                                    "name": "test19",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test20",
                                    "name": "test20",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                },
                                {
                                    "uuid": "test21",
                                    "name": "test21",
                                    "schedule_status": "2023-08-31",
                                    "total_runs": 12,
                                    "success_count": 10,
                                    "fail_count": 2
                                }
                            ]})
    except MinimalETLException as excep:
        logger.error("GET /pipelines_summary - %s", excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.get("/test")
async def test_api():
    """test endpoint"""
    try:
        logger.info("GET /test")
        async with transaction():
            repo = PipelineExecutionEntity()
            item = await repo.update(key="id", value=1, payload={"status": "CANCELLED"})
            logger.info(item)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": "ok"})
    except MinimalETLException as excep:
        logger.error("GET /summary - %s", excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.get("/summary")
async def get_summary() -> JSONResponse:
    """ endpoint to fetch summary
    """
    try:
        logger.info("GET /summary")
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"summary": await PipelineService.get_pipelines_summary()})
    except MinimalETLException as excep:
        logger.error("GET /summary - %s", excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.get("/pipeline/{uuid}")
async def get_pipeline_by_uuid(uuid: str) -> JSONResponse:
    """ endpoint to fetch pipline from uuid

    Args:
        uuid (str): uuid of the pipeline

    """
    try:
        logger.info("GET /pipeline/%s", uuid)
        pipeline = await PipelineService.get_pipeline_from_uuid(uuid)
        logger.info("GET /pipeline/%s %s", uuid, status.HTTP_200_OK)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"pipeline": pipeline})
    except MinimalETLException as excep:
        logger.error("GET /pipeline/%s %s", uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.delete("/pipeline/{uuid}")
async def delete_pipeline(uuid: str) -> JSONResponse:
    """ endpoint to delete pipeline

    Args:
        uuid (str): uuid of the pipeline

    """
    try:
        logger.info("DELETE /pipeline/%s", uuid)
        pipeline = await PipelineService.delete_pipeline_by_uuid(uuid)

        return JSONResponse(status_code=status.HTTP_200_OK, content={"pipeline": pipeline})
    except MinimalETLException as excep:
        logger.error("DELETE /pipeline/%s %s", uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.get("/pipelines")
async def get_pipeline_list() -> JSONResponse:
    """ endpoint to fetch list of pipelines

    """
    try:
        logger.info("GET /pipelines")
        pipelines = await PipelineService.get_all_pipelines_from_repo()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"pipelines": pipelines})

    except MinimalETLException as excep:
        logger.error("GET /pipelines %s", excep.args)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": excep.args})


@api_router.post("/pipeline")
async def add_pipeline(pipeline_config: PipelineModel) -> JSONResponse:
    """ endpoint to create and register pipeline in the repo

    Args:
        pipeline_config (PipelineModel)

    """
    try:
        logger.info("POST /pipeline %s", pipeline_config.name)
        pipeline = await PipelineService.create_pipeline(
            pipeline_config.name,pipeline_config.executor_type, 
            pipeline_config.executor_config, pipeline_config.description)

        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"pipeline": pipeline})
    except MinimalETLException as excep:
        logger.error("POST /pipeline %s", pipeline_config)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.put("/pipeline/{uuid}")
async def update_pipeline(uuid: str, pipeline_config: PipelineUpdateModel) -> JSONResponse:
    """ endpoint to update exixting pipeline

    Args:
        pipeline_config (PipelineModel)

    """
    try:
        logger.info("PUT /pipeline/%s", uuid)
        pipeline = await PipelineService.update_pipeline(
            uuid, pipeline_config)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"pipeline": pipeline})
    except MinimalETLException as excep:
        logger.error("PUT /pipeline/%s", uuid)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.post("/pipeline/{uuid}/task")
async def add_task(uuid: str, task_config: TaskModel) -> JSONResponse:
    """ endpoint to add task to a pipeline

    Args:
        uuid (str): uuid of the pipeline
        task_config (TaskModel): configurations of the task to be added
    """
    try:
        logger.info("POST /pipeline/%s/task %s", uuid, task_config.name)
        task = await TaskService.add_task_to_pipeline(uuid, task_config)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"pipeline": task})
    except MinimalETLException as excep:
        logger.error("POST /pipeline/%s/task %s", uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.get("/pipeline/{pipeline_uuid}/task/{task_uuid}")
async def get_task_by_uuid(pipeline_uuid: str, task_uuid: str) -> JSONResponse:
    """ endpoint to get task from a pipeline

    Args:
        pipeline_uuid (str): uuid of the pipeline
        task_uuid (str): uuid of the task
    """
    try:
        logger.info("GET /pipeline/%s/task/%s", pipeline_uuid, task_uuid)
        task = await TaskService.get_task(pipeline_uuid, task_uuid)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'task': task})

    except MinimalETLException as excep:
        logger.error("GET /pipeline/%s/task/%s %s",
                     pipeline_uuid, task_uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.get("/pipeline/{uuid}/tasks")
async def get_all_tasks_by_pipeline(uuid: str) -> JSONResponse:
    """ endpoint to fetch all the tasks from a pipeline

    Args:
        uuid (str): uuid of the pipeline
    """
    try:
        logger.info("GET /pipeline/%s/tasks", uuid)
        tasks = await TaskService.get_all_tasks(uuid)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'pipeline': uuid, 'tasks': tasks})

    except MinimalETLException as excep:
        logger.error("GET /pipeline/%s/tasks %s", uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.get("/sample_data")
async def get_sample_records(pipeline_uuid: str, task_uuid: str) -> JSONResponse:
    """endpoint to get sample records from executed task

    Args:
        pipeline_uuid (str): uuid of the pipeline
        task_uuid (str): uuid of the task
    """
    try:
        logger.info("GET /sample_data - pipeline %s - task %s",
                    pipeline_uuid, task_uuid)
        data = await TaskService.get_sample_records(pipeline_uuid, task_uuid)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=data)
    except Exception as excep:
        logger.error("GET /sample_data - pipeline %s - task %s | %s",
                     pipeline_uuid, task_uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.delete("/pipeline/{pipeline_uuid}/task/{task_uuid}")
async def delete_task_by_uuid(pipeline_uuid: str, task_uuid: str) -> JSONResponse:
    """ endpoint to delete task from a pipeline

    Args:
        pipeline_uuid (str): uuid of pipeline
        task_uuid (str): uuid of task
    """
    try:
        logger.info("DELETE /pipeline/%s/task/%s", pipeline_uuid, task_uuid)
        task = await TaskService.delete_task(pipeline_uuid, task_uuid)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'pipeline': pipeline_uuid, 'task': task, 'deleted': True})

    except MinimalETLException as excep:
        logger.error("DELETE /pipeline/%s/tasks %s | %s",
                     pipeline_uuid, task_uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.put("/pipeline/{pipeline_uuid}/task/{task_uuid}")
async def update_task(pipeline_uuid: str, task_uuid: str,
                      request: Request) -> JSONResponse:
    """ endpoint to update task properties

    Args:
        pipeline_uuid (str): uuid of the pipeline
        task_uuid (str): uuid of the task
        request (TaskUpdateModel): properties of the task to be updated

    """

    try:
        logger.info("PUT /pipeline/%s/task/%s", pipeline_uuid, task_uuid)
        pipeline = await TaskService.update_task_by_config(pipeline_uuid, task_uuid, request)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'pipeline': pipeline})

    except MinimalETLException as excep:
        logger.error("PUT /pipeline/%s/task/%s | %s",
                     pipeline_uuid, task_uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.get("/pipeline/{pipeline_uuid}/execute")
async def execute_pipeline(pipeline_uuid: str) -> JSONResponse:
    """endpoint to trigger pipline execution

    Args:
        pipeline_uuid (str): uuid of the pipeline

    """
    try:
        logger.info("executing pipeline - %s", pipeline_uuid)
        async with transaction():
            execution_details = await PipelineService.execute_pipeline_by_uuid(
                pipeline_uuid)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"execution_details": execution_details})

    except MinimalETLException as excep:
        logger.error("/pipeline/%s/execute | %s", pipeline_uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.post("/pipeline/{pipeline_uuid}/schedule")
async def schedule_job(pipeline_uuid: str, cron_time: CronModel):
    """endpoint to schedule pipeline esecution

    Args:
        pipeline_uuid (str): uuid of the pipeline
        cron_time (CronModel): schedule time in cron expression
    """
    try:
        logger.info("GET /pipeline/%s/schedule", pipeline_uuid)

        await PipelineService.schedule(pipeline_uuid, cron_time)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'status': "scheduled"})
    except MinimalETLException as excep:
        logger.error("GET /pipeline/%s/schedule",
                     pipeline_uuid)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})
