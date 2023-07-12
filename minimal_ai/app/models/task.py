import json
import logging
from dataclasses import field
from typing import Any, Dict, List

import polars as pl
from pydantic.dataclasses import dataclass

from minimal_ai.app.services.db_service import DBService
from minimal_ai.app.services.file_service import FileService
from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.services.transformer import PythonTransformer
from minimal_ai.app.utils import *

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class Task:
    uuid: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.NOT_EXECUTED
    pipeline: Any = None
    executor_config: Dict[Any, Any] = field(default_factory=dict)
    upstream_tasks: List[str] = field(default_factory=list)
    downstream_tasks: List[str] = field(default_factory=list)

    @property
    def all_upstream_task_executed(self):
        """
        Task property to check if all upstream task is executed
        """
        _executed = True
        for task_uuid in self.upstream_tasks:
            _task = self.pipeline.tasks[task_uuid]
            if _task['status'] != "executed":
                _executed = False
                break
        return _executed

    @classmethod
    def create(cls,
               name: str,
               task_type: str,
               executor_config=None,
               pipeline=None,
               priority: int | None = None,
               upstream_task_uuids=None) -> 'Task':
        """method to add task to a pipeline

        Args:
            name (str): task name
            task_type (TaskType): type of the task
            executor_config (Dict, optional): configurations related to the task. Defaults to None.
            pipeline (Pipeline, optional): pipeline. Defaults to None.
            priority (int | None, optional): priority of the task in the pipeline. Defaults to None.
            upstream_task_uuids (_type_, optional): _description_. Defaults to None.
        """
        if upstream_task_uuids is None:
            upstream_task_uuids = []

        # if executor_config is None:
        #     executor_config = {}

        uuid = clean_name(name)
        logger.info('Creating task - %s', uuid)
        if pipeline is not None and pipeline.has_task(uuid):
            logger.error(
                'Task - %s already present in pipeline - %s', uuid, pipeline.uuid)
            raise MinimalETLException(
                f'Task {uuid} already exists. Please use a different name.')

        logger.info('Task - %s is of type %s', uuid, task_type)

        task = cls.task_class_from_type(task_type)(
            uuid=uuid,
            task_type=TaskType(task_type),
            pipeline=pipeline,
            executor_config=executor_config)

        task.after_create(
            pipeline=pipeline,
            priority=priority,
            upstream_task_uuids=upstream_task_uuids,
        )
        return task

    def after_create(self, **kwargs) -> None:
        """ method to add task to corresponding pipeline
        """
        if kwargs.get('upstream_task_uuids') is not None:
            self.upstream_tasks.extend(kwargs.get(  # type: ignore
                'upstream_task_uuids'))
        self.update_upstream_tasks(
            add_to_task_uuids=kwargs.get('upstream_task_uuids'))
        pipeline = kwargs.get('pipeline')
        if pipeline is not None:
            priority = kwargs.get('priority')

            pipeline.add_task(
                self,
                priority=priority,
            )

    def update_upstream_tasks(self, add_to_task_uuids=None, remove_from_task_uuids=None) -> None:
        """ method to update the upstream tasks of current task

        Args:
            add_to_task_uuids (list, optional): upstream tasks to update. Defaults to [].
            remove_from_task_uuids (list, optional): upstream tasks to update. Defaults to [].

        Raises:
            MinimalETLException: upstream task not defined in pipeline
        """

        if add_to_task_uuids is None:
            add_to_task_uuids = []
        if remove_from_task_uuids is None:
            remove_from_task_uuids = []
        if add_to_task_uuids:
            logger.debug(add_to_task_uuids)
            for task_uuid in add_to_task_uuids:
                if not self.pipeline.has_task(task_uuid):
                    logger.error(
                        'Task - %s not defined in pipeline - %s', task_uuid, self.pipeline.uuid)
                    raise MinimalETLException(
                        f'Task - {task_uuid} not defined in pipeline - {self.pipeline.uuid}')
                self.pipeline.tasks[task_uuid]['downstream_tasks'].append(
                    self.uuid)

        if remove_from_task_uuids:
            logger.debug(remove_from_task_uuids)
            for task_uuid in remove_from_task_uuids:
                if not self.pipeline.has_task(task_uuid):
                    logger.error(
                        'Task - %s not defined in pipeline - %s', task_uuid, self.pipeline.uuid)
                    raise MinimalETLException(
                        f'Task - {task_uuid} not defined in pipeline - {self.pipeline.uuid}')
                self.pipeline.tasks[task_uuid]['downstream_tasks'].remove(
                    self.uuid)

    @classmethod
    def get_task_from_config(cls, task_config: Dict, _pipeline):
        """ class method to get the task object from config

        Args:
            task_config (Dict): config of task properties
            _pipeline (Pipeline): pipeline object

        Raises:
            MinimalETLException

        Returns:
            Task: object of class task
        """
        # task_config.pop('all_upstream_task_executed')
        task = cls.task_class_from_type(
            task_config['task_type'])(**task_config)  # type: ignore
        task.pipeline = _pipeline
        return task

    @classmethod
    def task_class_from_type(cls, task_type: str) -> 'Task':
        """ method to determine task class on the basis of task type

        Args:
            task_type (str): type of the task

        Returns:
            Task
        """
        match task_type:
            case TaskType.DATA_LOADER:
                return DataLoaderTask  # type: ignore
            case TaskType.DATA_SINK:
                return DataSinkTask  # type: ignore
            case TaskType.DATA_TRANSFORMER:
                return DataTransformerTask  # type: ignore
            case _:
                raise MinimalETLException(
                    f'Task type - {task_type} not supported')


@dataclass(kw_only=True)
class DataLoaderTask(Task):
    loader_type: LoaderType | None = None
    loader_config: Dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.loader_config = {} if self.loader_config is None else self.loader_config
        self.executor_config = {} if self.executor_config is None else self.executor_config
        self.upstream_tasks = [] if self.upstream_tasks is None else self.upstream_tasks
        self.downstream_tasks = [] if self.downstream_tasks is None else self.downstream_tasks

    def base_dict_obj(self) -> Dict:
        """ method to get task dict object
        """
        return {
            'uuid': self.uuid,
            'status': self.status,
            'task_type': self.task_type,
            'executor_config': self.executor_config,
            'upstream_tasks': self.upstream_tasks,
            'downstream_tasks': self.downstream_tasks,
            'loader_type': self.loader_type,
            'loader_config': self.loader_config
        }

    def validate_configurations(self, loader_type: str, loader_config: Dict):
        """ method to configure task loader

        Args:
            loader_type (str): type of the loader
            loader_config (Dict): properties of the loader

        """
        try:
            loader = LoaderType(loader_type)

            match loader:
                case "db":
                    _config = DBConfig.parse_obj(loader_config)
                    logger.debug(_config)
                    logger.info('Configuring %s loader for task - %s',
                                loader_type, self.uuid)
                    self.loader_type = loader
                    self.loader_config = _config.dict()

                case "file":
                    _config = FileConfig.parse_obj(loader_config)
                    logger.debug(_config)
                    logger.info('Configuring %s loader for task - %s',
                                loader_type, self.uuid)
                    self.loader_type = loader
                    self.loader_config = _config.dict()

                case _:
                    logger.error('Loader type - %s not supported', loader_type)
                    raise MinimalETLException(
                        f'Loader type - {loader_type} not supported')
        except Exception as excep:
            logger.error('Loader type - %s not supported | %s',
                         loader_type, excep.args)
            raise MinimalETLException(
                f'Loader type - {loader_type} not supported | {excep.args}')

    async def execute(self, show_sample: bool = False, sample_count: int = 0) -> Dict:
        """
        async method to execute the task
        Args:
            show_sample (bool): whether to return the output dataframe
            sample_count (): number of rows of the dataframe

        """
        logger.info("Executing task - %s", self.uuid)

        if not self.all_upstream_task_executed:
            self.status = TaskStatus.FAILED
            logger.error(
                'Not all upstream tasks have been executed. Please execute them first')
            raise MinimalETLException(
                'Not all upstream tasks have been executed. Please execute them first')

        match self.loader_type:
            case "db":
                _config: Dict = self.loader_config
                db_conn = DBService.get_db_conn(_config)
                loaded_data = DBService.load_source(db_conn, _config['table'])

            case "file":
                _config: Dict = self.loader_config
                file_path = self.pipeline.variable_dir
                loaded_data = FileService.load_source(_config, file_path)

            case _:
                self.status = TaskStatus.FAILED
                logger.error('Loader type - %s not supported',
                             self.loader_type)
                raise MinimalETLException(
                    f'Loader type - {self.loader_type} not supported')

        self.status = TaskStatus.EXECUTED

        self.pipeline.variable_manager.add_variable(
            self.pipeline.uuid,
            self.uuid,
            self.uuid,
            loaded_data,
            VariableType.PYTHON_DATAFRAME
        )

        if show_sample:
            logger.debug(loaded_data)
            return {
                'task': self.base_dict_obj(),
                'output': json.loads(loaded_data.head(sample_count).write_json(row_oriented=True))
            }
        return {
            'task': self.base_dict_obj(),
            'executed': self.status
        }


@dataclass(kw_only=True)
class DataSinkTask(Task):
    sink_type: SinkType | None = None
    sink_config: Dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.sink_config = {} if self.sink_config is None else self.sink_config
        self.executor_config = {} if self.executor_config is None else self.executor_config
        self.upstream_tasks = [] if self.upstream_tasks is None else self.upstream_tasks
        self.downstream_tasks = [] if self.downstream_tasks is None else self.downstream_tasks

    def base_dict_obj(self) -> Dict:
        """ method to get task dict object
        """
        return {
            'uuid': self.uuid,
            'status': self.status,
            'task_type': self.task_type,
            'executor_config': self.executor_config,
            'upstream_tasks': self.upstream_tasks,
            'downstream_tasks': self.downstream_tasks,
            'sink_type': self.sink_type,
            'sink_config': self.sink_config
        }

    async def execute(self, show_sample: bool = False, sample_count: int = 0) -> Dict:
        """method to execute task

        Args:
            show_sample (bool): wether to show output, default is False
            sample_count (int): count of records to be shown, default is 0

        Raises:
            MinimalETLException

        Returns:
            Dict: task information along with sample data
        """
        logger.info("Executing task - %s", self.uuid)
        if not self.all_upstream_task_executed:
            self.status = TaskStatus.FAILED
            logger.error(
                'Not all upstream tasks have been executed. Please execute them first')
            raise MinimalETLException(
                'Not all upstream tasks have been executed. Please execute them first')

        if len(self.upstream_tasks) != 1:
            self.status = TaskStatus.FAILED
            logger.error(
                "Task type - %s must have only 1 upstream task configured", self.task_type)
            raise MinimalETLException(
                f"Task type - {self.task_type} must have only 1 upstream task configured")

        target_data: pl.DataFrame = await self.pipeline.variable_manager.get_variable_data(self.upstream_tasks[0])
        # loaded_data = pl.DataFrame
        match self.sink_type:
            case "db":
                _config: Dict = self.sink_config
                db_conn = DBService.get_db_conn(_config)
                DBService.ingest_data(
                    db_conn, _config['table'], target_data.to_pandas(), self.sink_config['ingestion_type'])

            case _:
                self.status = TaskStatus.FAILED
                logger.error('Sink type - %s not supported', self.sink_type)
                raise MinimalETLException(
                    f'Sink type - {self.sink_type} not supported')

        self.status = TaskStatus.EXECUTED

        if show_sample:
            return {
                'task': self.base_dict_obj(),
                'sample': json.loads(target_data.head(sample_count).write_json(row_oriented=True))
            }
        return {
            'task': self.base_dict_obj()
        }

    def validate_configurations(self, sink_type: str, sink_config: Dict):
        """ method to configure task loader

        Args:
            sink_type (str): type of the sink
            sink_config (Dict): properties of the sink

        """

        try:
            sink = SinkType(sink_type)

            match sink:
                case "db":
                    _config = DBConfig.parse_obj(sink_config)
                    logger.debug(_config)
                    logger.info('Configuring %s sink for task - %s',
                                sink_type, self.uuid)
                    self.sink_type = sink
                    self.sink_config = _config.dict()

                case "file":
                    _config = FileConfig.parse_obj(sink_config)
                    logger.debug(_config)
                    logger.info('Configuring %s sink for task - %s',
                                sink_type, self.uuid)
                    self.sink_type = sink
                    self.sink_config = _config.dict()

                case _:
                    logger.error('Sink type - %s not supported', sink_type)
                    raise MinimalETLException(
                        f'Sink type - {sink_type} not supported')
        except Exception as excep:
            logger.error('Sink type - %s not supported | %s',
                         sink_type, excep.args)
            raise MinimalETLException(
                f'Sink type - {sink_type} not supported | {excep.args}')


@dataclass(kw_only=True)
class DataTransformerTask(Task):
    transformer_type: TransformerType | None = None
    transformer_config: Dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.transformer_config = {} if self.transformer_config is None else self.transformer_config
        self.executor_config = {} if self.executor_config is None else self.executor_config
        self.upstream_tasks = [] if self.upstream_tasks is None else self.upstream_tasks
        self.downstream_tasks = [] if self.downstream_tasks is None else self.downstream_tasks

    def base_dict_obj(self) -> Dict:
        """ method to get task dict object
        """
        return {
            'uuid': self.uuid,
            'status': self.status,
            'task_type': self.task_type,
            'executor_config': self.executor_config,
            'upstream_tasks': self.upstream_tasks,
            'downstream_tasks': self.downstream_tasks,
            'transformer_type': self.transformer_type,
            'transformer_config': self.transformer_config
        }

    def validate_configurations(self, transformer_type: str, transformer_config: Dict):
        """ method to configure task loader

        Args:
            transformer_type (str): type of the sink
            transformer_config (Dict): properties of the sink

        """

        try:
            transformer = TransformerType(transformer_type)
            logger.debug(transformer)
            match transformer:
                case "filter":
                    _config = FilterModel.parse_obj(transformer_config)
                    logger.debug(_config)
                    logger.info('Configuring %s transformer for task - %s',
                                transformer_type, self.uuid)
                    self.transformer_type = transformer
                    self.transformer_config = _config.dict()

                case "join":
                    _config = JoinModel.parse_obj(transformer_config)
                    logger.debug(_config)
                    logger.info('Configuring %s transformer for task - %s',
                                transformer_type, self.uuid)
                    self.transformer_type = transformer
                    self.transformer_config = _config.dict()

                case "union":
                    logger.info('Configuring %s transformer for task - %s',
                                transformer_type, self.uuid)
                    self.transformer_type = transformer

                case "pivot":
                    _config = PivotModel.parse_obj(transformer_config)
                    logger.info('Configuring %s transformer for task - %s',
                                transformer_type, self.uuid)
                    self.transformer_type = transformer
                    self.transformer_config = _config.dict()

                case _:
                    logger.error(
                        'Transformer type - %s not supported', transformer_type)
                    raise MinimalETLException(
                        f'Transformer type - {transformer_type} not supported')
        except Exception as excep:
            logger.error('Transformer type - %s not supported | %s',
                         transformer_type, excep.args)
            raise MinimalETLException(
                f'Transformer type - {transformer_type} not supported | {excep.args}')

    async def execute(self, show_sample: bool = False, sample_count: int = 0) -> Dict:
        """method to execute task

        Args:
            show_sample (bool): wether to show output, default is Fasle
            sample_count (int): count of records to be shown, default is 0

        Raises:
            MinimalETLException

        Returns:
            Dict: task information along with sample data
        """
        logger.info("Executing task - %s", self.uuid)
        if not self.all_upstream_task_executed:
            self.status = TaskStatus.FAILED
            logger.error(
                'Not all upstream tasks have been executed. Please execute them first')
            raise MinimalETLException(
                'Not all upstream tasks have been executed. Please execute them first')

        match self.pipeline.executor_type:
            case "python":
                target_data = await PythonTransformer(current_task=self).transform()
            # case "pyspark":
            #     pass
            case _:
                self.status = TaskStatus.FAILED
                logger.error('Executor type - %s not supported',
                             self.pipeline.executor_type)
                raise MinimalETLException(
                    f'Executor type - {self.pipeline.executor_type} not supported')

        self.status = TaskStatus.EXECUTED

        self.pipeline.variable_manager.add_variable(
            self.pipeline.uuid,
            self.uuid,
            self.uuid,
            target_data,
            VariableType.PYTHON_DATAFRAME
        )

        if show_sample:
            return {
                'task': self.base_dict_obj(),
                'sample': json.loads(target_data.head(sample_count).write_json(row_oriented=True))
            }
        return {
            'task': self.base_dict_obj()
        }