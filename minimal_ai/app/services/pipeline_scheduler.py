import logging
from functools import lru_cache

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.models.pipeline import Pipeline
from minimal_ai.app.utils.constants import CronModel, PipelineStatus

logger = logging.getLogger(__name__)

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': ThreadPoolExecutor(settings.THREAD_POOL_EXECUTOR),
    'processpool': ProcessPoolExecutor(settings.PROCESS_POOL_EXECUTOR)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}


@lru_cache
def get_scheduler_obj() -> BackgroundScheduler:
    """method to create the scheduler object and return it

    Returns:
        BackgroundScheduler: scheduler object
    """
    logger.debug(jobstores)
    scheduler = BackgroundScheduler(
        jobstores=jobstores, executors=executors, job_defaults=job_defaults)
    logger.info(scheduler)
    return scheduler


def start_scheduler(scheduler: BackgroundScheduler) -> None:
    """method to start the scheduler

    Args:
        scheduler (BackgroundScheduler): scheduler instance
    """
    if scheduler.running:
        logger.info("Scheduler already in running state")
    else:
        scheduler.start()
        # scheduler.add_job(PipelineService.execute_pipeline_by_uuid, args=["customer_pipeline"],
        #                   trigger='cron', year='*', month='*', day='*', week='*', day_of_week='*', hour=2,
        #                   minute=16, second=0)
        # scheduler.print_jobs()


def stop_scheduler(scheduler: BackgroundScheduler) -> None:
    """method to stop the scheduler

    Args:
        scheduler (BackgroundScheduler): scheduler instance
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stoped")
    else:
        logger.info("scheduler not running")


def schedule_pipeline(pipeline_uuid: str, cron_time: CronModel, func):
    """method to schedule pipeline execution

    Args:
        pipeline_uuid (str): uuid of pipeline
        cron_time (str): cron expression
    """
    pipeline = Pipeline.get_pipeline(pipeline_uuid)
    logger.info("scheduling - %s for execution", pipeline_uuid)
    scheduler = get_scheduler_obj()
    cron = CronTrigger(**cron_time.dict())
    logger.debug(cron)
    scheduler.add_job(func, args=[pipeline_uuid],
                      trigger=cron, id=pipeline_uuid)
    pipeline.status = PipelineStatus.SCHEDULED
    pipeline.save()
