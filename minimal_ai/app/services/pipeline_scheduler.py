import logging
from functools import lru_cache

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils.constants import CronModel

logger = logging.getLogger(__name__)

jobstores = {
    "default": SQLAlchemyJobStore(
        url=settings.MINIMAL_SYNC_DATABASE_URL,
        tablename=settings.MINIMAL_SCHEDULER_TABLE,
    )
}
executors = {
    "threadpool": ThreadPoolExecutor(settings.THREAD_POOL_EXECUTOR),
    "processpool": ProcessPoolExecutor(settings.PROCESS_POOL_EXECUTOR),
}
job_defaults = {"coalesce": False, "max_instances": 3}


@lru_cache
def get_scheduler() -> BackgroundScheduler:
    """method to create the scheduler object and return it

    Returns:
        BackgroundScheduler: scheduler object
    """
    scheduler = BackgroundScheduler(
        jobstores=jobstores, executors=executors, job_defaults=job_defaults
    )
    logger.info(scheduler)
    return scheduler


async def schedule_pipeline(pipeline_uuid: str, cron_time: CronModel, func):
    """method to schedule pipeline execution

    Args:
        pipeline_uuid (str): uuid of pipeline
        cron_time (str): cron expression
    """
    try:
        logger.info("scheduling - %s for execution", pipeline_uuid)

        scheduler = get_scheduler()
        cron = CronTrigger(**cron_time.model_dump())

        scheduler.add_job(func, args=[pipeline_uuid], trigger=cron, id=pipeline_uuid)

    except Exception as excep:
        logger.error("Error while scheduling pipeline - %s", pipeline_uuid)
        raise MinimalETLException(
            f"Error while scheduling pipeline - {pipeline_uuid} | {excep.args}"
        )
