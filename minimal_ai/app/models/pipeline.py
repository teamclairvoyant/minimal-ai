import asyncio
import json
import logging
import os
import shutil
from queue import Queue
from typing import Any, Dict, List

import aiofiles
from pydantic.dataclasses import dataclass
from pydantic.fields import Field

from minimal_ai.app.api.api_config import settings
from minimal_ai.app.models.task import Task
from minimal_ai.app.models.variable import VariableManager
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.spark_main import SparkMain
from minimal_ai.app.utils.constants import PIPELINES_FOLDER, ScheduleStatus
from minimal_ai.app.utils.string_utils import clean_name, format_enum

METADATA_FILE = 'metadata.json'
VARIABLE_DIR = '.variable'
logger = logging.getLogger(__name__)


@dataclass
class Pipeline:
    uuid: str
    name: str | None = None
    tasks: Dict[Any, Any] = Field(default_factory=Dict)
    executor_config: Dict[Any, Any] = Field(default_factory=Dict)
    config: Dict | None = None
    schedule_status: ScheduleStatus = ScheduleStatus.NOT_SCHEDULED

    def __post_init__(self):
        """
        method to run post object creation
        Returns: None

        """
        self.config = self.load_config_file(
        ) if self.config is None else self.load_config(self.config)

    @property
    def config_dir(self):
        """
        path to config file for the pipeline
        """
        return os.path.join(settings.REPO_PATH, PIPELINES_FOLDER, self.uuid)

    @property
    def variable_dir(self):
        """
        path to variable dir
        """
        return os.path.join(self.config_dir, VARIABLE_DIR)

    @property
    def variable_manager(self):
        """
        variable manager for the pipeline
        """
        return VariableManager.get_manager(self.variable_dir)

    def load_config_file(self) -> None:
        """
        method to load configurations from config pipeline
        Returns: Dict

        """
        logger.info('Reading config file for pipeline %s', self.uuid)
        if not os.path.exists(self.config_dir):
            logger.error("Pipeline %s doesn't exists", self.uuid)
            raise MinimalETLException(
                f"Pipeline - {self.uuid} doesn't exists")

        with open(os.path.join(self.config_dir, METADATA_FILE)) as _file:
            _config = json.load(_file)

        self.load_config(_config)

    def load_config(self, _config: Dict) -> None:
        """
        method to load json metadata file
        Returns:

        """
        self.name = _config.get('name')
        self.uuid = _config.get('uuid')  # type: ignore
        self.executor_config = _config.get('executor_config', {})
        self.tasks = _config.get('tasks', {})
        self.schedule_status = ScheduleStatus(_config.get('schedule_status'))

    def base_obj(self) -> Dict:
        """
        method to get the Pipeline object dictionary
        Returns: Dict -> pipeline

        """
        return {
            "name": self.name,
            "uuid": self.uuid,
            "executor_config": self.executor_config,
            "tasks": self.tasks,
            "schedule_status": self.schedule_status
        }

    @classmethod
    def create(cls, name: str, executor_config: Dict[str, str]) -> 'Pipeline':
        """
        method to create object pipeline class
        Args:
            name (str): name of the pipeline
            executor_config (Dict): spark config of the pipeline

        Returns:

        """
        logger.info("creating pipeline %s", name)
        uuid = clean_name(name)
        pipeline_path = os.path.join(
            settings.REPO_PATH, PIPELINES_FOLDER, uuid)
        variable_path = os.path.join(pipeline_path, VARIABLE_DIR)

        if os.path.exists(pipeline_path):
            logger.error('Pipeline %s already exists.', name)
            raise MinimalETLException(f'Pipeline - {name} already exists.')
        os.makedirs(pipeline_path)
        os.makedirs(variable_path)

        logger.debug('pipeline dir -> %s', pipeline_path)
        logger.debug('variable dir -> %s', variable_path)

        with open(os.path.join(pipeline_path, METADATA_FILE), 'w') as config_file:
            json.dump({
                "name": name,
                "uuid": uuid,
                "executor_config": executor_config,
                "schedule_status": format_enum(ScheduleStatus.NOT_SCHEDULED)
            }, config_file, indent=4)

        pipeline = Pipeline(uuid=uuid)

        return pipeline

    @classmethod
    async def get_pipeline_async(cls, uuid: str) -> 'Pipeline':
        """ method to get pipeline object from uuid

        Args:
            uuid (str): uuid of pipeline

        Returns:
            Pipeline
        """

        config_path = os.path.join(
            settings.REPO_PATH,
            PIPELINES_FOLDER,
            uuid,
            METADATA_FILE,
        )

        if not os.path.exists(config_path):
            logger.error('Pipeline %s does not exist.', uuid)
            raise MinimalETLException(f'Pipeline - {uuid} does not exist.')
        async with aiofiles.open(config_path, mode='r') as config_file:
            try:
                logger.info("Loading Pipeline %s", uuid)
                config = json.loads(await config_file.read()) or {}
            except Exception as err:
                config = {}
                logger.info(err)

        pipeline = cls(uuid=uuid, config=config)

        return pipeline

    @classmethod
    def get_pipeline(cls, uuid: str) -> 'Pipeline':
        """ method to get pipeline object from uuid

        Args:
            uuid (str): uuid of pipeline

        Returns:
            Pipeline
        """

        config_path = os.path.join(
            settings.REPO_PATH,
            PIPELINES_FOLDER,
            uuid,
            METADATA_FILE,
        )

        if not os.path.exists(config_path):
            logger.error('Pipeline %s does not exist.', uuid)
            raise MinimalETLException(f'Pipeline - {uuid} does not exist.')
        with open(config_path, 'r') as config_file:
            try:
                logger.info("Loading Pipeline %s", uuid)
                config = json.load(config_file) or {}
            except Exception as err:
                config = {}
                logger.info(err)

        pipeline = cls(uuid=uuid, config=config)

        return pipeline

    @classmethod
    def get_all_pipelines(cls) -> List:
        """ method to fetch all the pipelines from the repo

        Returns:
            List[pipeline]
        """
        logger.info("Fetching pipelines from the repo")
        if not os.path.exists(settings.PIPELINES_DIR):
            os.mkdir(settings.PIPELINES_DIR)
        return [
            d
            for d in os.listdir(settings.PIPELINES_DIR)
            if cls.is_valid_pipeline(os.path.join(settings.PIPELINES_DIR, d))
        ]

    @classmethod
    def is_valid_pipeline(cls, pipeline_path) -> bool:
        """ method to check id the pipeline is valid or not

        Args:
            pipeline_path (str): path to pipeline dir

        Returns:
            bool
        """
        return os.path.isdir(pipeline_path) and os.path.exists(
            os.path.join(pipeline_path, METADATA_FILE)
        )

    def delete(self):
        """ method to delete the pipeline
        """
        logger.info("Deleting Pipeline - %s", self.uuid)
        shutil.rmtree(self.config_dir)

    def has_task(self, task_uuid: str) -> bool:
        """method to check if task exists in pipeline

        Args:
            task_uuid (str): uuid of the task
        """

        return task_uuid in self.tasks

    def add_task(self, task, priority=None) -> Any:
        """ method to attach task to pipeline

        Args:
            task
            priority

        """

        if priority is None or priority > len(self.tasks.keys()):
            self.tasks[task.uuid] = task.base_dict_obj()
        else:
            task_list = list(self.tasks.items())
            task_list.insert(priority - 1, (task.uuid, task.base_dict_obj()))
            self.tasks = dict(task_list)
        logger.info('Added task - %s to the pipeline', task.uuid)
        # self.validate('A cycle was formed while adding a task')

        self.save()
        return task

    def save(self) -> None:
        """ method to save current pipeline
        """

        pipeline_dict = self.base_obj()
        try:
            with open(os.path.join(self.config_dir, METADATA_FILE), 'w') as file_config:
                json.dump(pipeline_dict, file_config, indent=4)

            logger.info('Pipeline - %s saved successfully', self.uuid)
        except Exception as excep:
            raise MinimalETLException(
                f'Pipeline - {self.uuid} failed to save | {excep.args}')

    async def execute(self, root_tasks: List) -> None:
        """method to execute the pipeline
        """
        def create_task(task_conf: Dict):
            async def build_and_execute():
                task = Task.get_task_from_config(task_conf, self)
                exec_data = await task.execute(spark)
                self.tasks[task_conf['uuid']] = exec_data['task']

            return asyncio.create_task(build_and_execute())
        spark, spark_config = SparkMain(self.uuid).start_spark()
        task_queue = Queue()
        executed_tasks = {}
        for _task in root_tasks:
            task_queue.put(_task)
            executed_tasks[_task] = None

        while not task_queue.empty():
            task_uuid = task_queue.get()
            task_conf = self.tasks[task_uuid]

            skip = False
            for upstream_task in task_conf['upstream_tasks']:
                if executed_tasks.get(upstream_task) is None:
                    task_queue.put(task_uuid)
                    skip = True
                    break
            if skip:
                continue

            upstream_tasks = [executed_tasks[uuid]
                              for uuid in task_conf['upstream_tasks']]
            await asyncio.gather(*upstream_tasks)

            task_stat = create_task(task_conf)
            executed_tasks[task_uuid] = task_stat
            for downstream_task in task_conf['downstream_tasks']:
                if downstream_task not in executed_tasks:
                    executed_tasks[downstream_task] = None
                    task_queue.put(downstream_task)
        remaining_tasks = filter(
            lambda task: task is not None, executed_tasks.values())
        await asyncio.gather(*remaining_tasks)
        spark.stop()
        self.save()
