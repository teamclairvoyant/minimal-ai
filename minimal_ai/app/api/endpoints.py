import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.pipeline_scheduler import schedule_pipeline
from minimal_ai.app.services.pipeline_service import PipelineService
from minimal_ai.app.services.task_service import TaskService
from minimal_ai.app.utils.constants import CronModel, PipelineModel, TaskModel

api_router = APIRouter()
logger = logging.getLogger(__name__)


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
        pipeline = PipelineService.create_pipeline(
            pipeline_config.name, pipeline_config.executor_config)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"pipeline": pipeline})
    except MinimalETLException as excep:
        logger.error("POST /pipeline %s", pipeline_config)
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
                            content={"task": task})
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
        task = await TaskService.update_task_by_config(pipeline_uuid, task_uuid, request)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'pipeline': pipeline_uuid, 'task': task})

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
        execution_details = await PipelineService.execute_pipeline_by_uuid(
            pipeline_uuid)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"execution_details": execution_details})

    except MinimalETLException as excep:
        logger.error("/pipeline/%s/execute | %s", pipeline_uuid, excep.args)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})


@api_router.post("/pipeline/{pipeline_uuid}/schedule")
async def schedule_task(pipeline_uuid: str, cron_time: CronModel):
    """endpoint to schedule pipeline esecution

    Args:
        pipeline_uuid (str): uuid of the pipeline
        cron_time (CronModel): schedule time in cron expression
    """
    try:
        logger.info("GET /pipeline/%s/schedule", pipeline_uuid)
        logger.debug(cron_time)
        schedule_pipeline(pipeline_uuid, cron_time,
                          PipelineService.scheduled_execution)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={'status': "scheduled"})
    except MinimalETLException as excep:
        logger.error("GET /pipeline/%s/schedule",
                     pipeline_uuid)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": excep.args})
