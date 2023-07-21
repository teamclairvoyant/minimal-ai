from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel

PIPELINES_FOLDER = 'pipelines'


class ScheduleStatus(str, Enum):
    """Schedule status class
    """
    SCHEDULED = 'scheduled'
    NOT_SCHEDULED = 'not_scheduled'


class TaskStatus(str, Enum):
    """ Block status class
    """
    EXECUTED = 'executed'
    FAILED = 'failed'
    NOT_EXECUTED = 'not_executed'
    UPDATED = 'updated'


class PipelineType(str, Enum):
    """
        Pipeline type to choose between pandas and pyspark
    """
    PYTHON = 'python'
    PYSPARK = 'pyspark'


class TaskType(str, Enum):
    """ supported task types
    """
    DATA_LOADER = 'data_loader'
    DATA_SINK = 'data_sink'
    DATA_TRANSFORMER = 'data_transformer'


class CronModel(BaseModel):
    """cron model
    """
    year: str
    month: str
    day: str
    week: str
    day_of_week: str
    hour: str
    minute: str
    second: str


class TaskModel(BaseModel):
    """ Model class to define Task
    """
    name: str
    task_type: str
    priority: int
    upstream_task_uuids: List[str] | None = None


class PipelineModel(BaseModel):
    """ Model class to define pipeline
    """
    name: str
    executor_config: Dict[Any, Any] | None = None


class VariableType(str, Enum):
    """ Supported variable types
    """
    PYTHON_DATAFRAME = 'python_dataframe'
    SPARK_DATAFRAME = 'spark_dataframe'


class LoaderType(str, Enum):
    """ Supported loader type """
    LOCAL_FILE = 'local_file'
    GS_FILE = 'gs_file'
    S3_FILE = 's3_file'
    RDBMS = 'rdbms'


class SinkType(str, Enum):
    """ Supported sink type """
    LOCAL_FILE = 'local_file'
    RDBMS = 'rdbms'
    GS_FILE = 'gs_file'
    S3_FILE = 's3_file'


class TransformerType(str, Enum):
    """ Supported transformer type """
    JOIN = 'join'
    UNION = 'union'
    PIVOT = 'pivot'
    FILTER = 'filter'
    SPARKAI = 'sparkAI'


class JoinModel(BaseModel):
    """
    properties for join type transformer
    """
    left_table: str
    right_table: str
    on: List[str]
    how: str


class FilterModel(BaseModel):
    """properties for filter transformer
    """
    prompt: str


class PivotModel(BaseModel):
    """properties for pivot transformer
    """
    index: List[str]
    columns: List[str]
    values: List[str]


class TaskUpdateModel(BaseModel):
    """ properties of task to be updated
    """
    upstream_task_uuids: List[str] | None = None
    config_type: str | None = None
    config_properties: Dict[str, Any] | None = None


class DBConfig(BaseModel):
    """ properties for the mysql connection
    """
    db_type: str
    host: str
    port: str
    user: str
    password: str
    database: str
    table: str
    ingestion_type: str | None = None


class FileConfig(BaseModel):
    """ properties for file type configurations
    """
    file_type: str
    file_path: str


class GSFileConfig(BaseModel):
    """ properties for file type configurations
    """
    bucket_name: str
    file_type: str
    file_path: str
