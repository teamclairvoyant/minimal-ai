import asyncio
import logging
from typing import Dict, List

from minimal_ai.app.models.pipeline import Pipeline
from minimal_ai.app.utils import TaskType

logger = logging.getLogger(__name__)


class PipelineService:

    @staticmethod
    def create_pipeline(name: str, executor_config: Dict[str, str] | None) -> Dict:
        """method to create the pipeline

        Args:
            name (str): name of the pipeline
            executor_config (Dict[str,str]): spark configurations

        Returns:
            Dict: created pipeline object
        """
        pipeline = Pipeline.create(name, executor_config)
        logger.info("Pipeline - %s created", name)
        return pipeline.base_obj()

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
        return pipeline.base_obj()

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
        return pipeline.base_obj()

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

        pipelines: List[Pipeline] = [
            pipeline for pipeline in _pipelines if pipeline is not None]

        collection = [pipeline.base_obj() for pipeline in pipelines]
        return collection

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
        return {"pipeline": pipeline_uuid, "status": "executed"}

    @staticmethod
    def scheduled_execution(pipeline_uuid: str) -> Dict:
        """method to trigger the scheduled execution

        Args:
            pipeline_uuid (str): uuid of the pipeline
        """
        pipeline = Pipeline.get_pipeline(pipeline_uuid)
        root_tasks = []
        logger.info("Loading data sources...")

        for task in pipeline.tasks:
            if pipeline.tasks[task]['task_type'] == TaskType.DATA_LOADER:
                root_tasks.append(task)

        asyncio.run(pipeline.execute(root_tasks))
        return {"pipeline": pipeline_uuid, "status": "executed"}
