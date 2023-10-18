import asyncio
import logging
from typing import Any, Dict, List

from minimal_ai.app.models.pipeline import Pipeline
from minimal_ai.app.services.database import CTX_SESSION, create_session
from minimal_ai.app.services.pipeline_scheduler import schedule_pipeline
from minimal_ai.app.utils import TaskType

logger = logging.getLogger(__name__)


class PipelineService:

    @staticmethod
    async def create_pipeline(name: str, executor_config: Dict[str, str] | None, description: str | None) -> Dict:
        """method to create the pipeline

        Args:
            name (str): name of the pipeline
            executor_config (Dict[str,str]): spark configurations
            description (str): short description for the pipeline
            db (Session): Database Session object
        Returns:
            Dict: created pipeline object
        """
        pipeline = Pipeline.create(name, executor_config, description)
        logger.info("Pipeline - %s created", name)
        return await pipeline.pipeline_summary()

    @staticmethod
    async def update_pipeline(pipeline_uuid: str, reactflow_props: Dict[Any, Any]) -> Dict:
        """method to update existing pipeline

        Args:
            pipeline_uuid (str): uuid of the pipeline
            reactflow_props (Dict[Any,Any]): reactflow object

        Returns:
            Dict: updated pipeline object
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        logger.info("Pipeline - %s fetched", pipeline_uuid)
        pipeline.add_reactflow_props(reactflow_props)

        return await pipeline.pipeline_summary()

    @staticmethod
    async def get_pipeline_from_uuid(uuid: str) -> Dict:
        """method to get pipeline from uuid

        Args:
            uuid (str): uuid of the pipeline

        Returns:
            Dict: pipeline object
        """
        pipeline = await Pipeline.get_pipeline_async(uuid)
        logger.info("Pipeline - %s fetched", uuid)
        return await pipeline.pipeline_summary()

    @staticmethod
    async def delete_pipeline_by_uuid(uuid: str) -> Dict:
        """method to delete pipeline by the uuid

        Args:
            uuid (str): uuid of the pipeline

        Returns:
            Dict: deleted pipeline object
        """

        pipeline = await Pipeline.get_pipeline_async(uuid)

        pipeline.delete()
        logger.info("Pipeline - %s deleted successfully", uuid)
        return await pipeline.pipeline_summary()

    @staticmethod
    async def get_all_pipelines_from_repo() -> List[Dict]:
        """method to fetch list of pipelines
        """

        pipeline_uuids = Pipeline.get_all_pipelines()

        async def get_pipeline(uuid):
            logger.info("Fetching details for pipeline - %s", uuid)
            return await Pipeline.get_pipeline_async(uuid)

        _pipelines = await asyncio.gather(
            *[get_pipeline(uuid) for uuid in pipeline_uuids]
        )

        pipelines = [
            await pipeline.pipeline_summary() for pipeline in _pipelines if pipeline is not None]

        return pipelines

    @staticmethod
    async def get_pipelines_summary() -> Dict[Any, Any]:
        """method to get summary of pipelines
        """
        summary = await Pipeline.summary()
        return summary

    @staticmethod
    async def execute_pipeline_by_uuid(pipeline_uuid: str) -> Dict:
        """method to trigger pipeline execution

        Args:
            pipeline_uuid (str): uuid of the pipeline
        """
        pipeline = Pipeline.get_pipeline(pipeline_uuid)
        root_tasks = []
        logger.info("Loading data sources...")

        for task in pipeline.tasks:
            if pipeline.tasks[task]['task_type'] == TaskType.DATA_LOADER:
                root_tasks.append(task)

        await pipeline.execute(root_tasks)

        return {"pipeline": pipeline_uuid, "status": "COMPLETED"}

    @staticmethod
    def scheduled_execution(pipeline_uuid: str):
        """method to trigger the scheduled execution

        Args:
            pipeline_uuid (str): uuid of the pipeline
        """
        db_sess = create_session()
        CTX_SESSION.set(db_sess)
        pipeline = Pipeline.get_pipeline(pipeline_uuid)
        root_tasks = []
        logger.info("Loading data sources...")

        for task in pipeline.tasks:
            if pipeline.tasks[task]['task_type'] == TaskType.DATA_LOADER:
                root_tasks.append(task)

        asyncio.run(pipeline.scheduled_execute(root_tasks))
        asyncio.run(db_sess.commit())
        asyncio.run(db_sess.close())

    @staticmethod
    async def schedule(pipeline_uuid: str, cron_time):
        """method to schedule pipeline for execution

        Args:
            pipeline_uuid (str): uuid of the pipeline
            cron_time (_type_): execution time in cron expression
        """
        pipeline = await Pipeline.get_pipeline_async(pipeline_uuid)
        await schedule_pipeline(pipeline_uuid, cron_time, PipelineService.scheduled_execution)
        pipeline.scheduled = True
        pipeline.save()
