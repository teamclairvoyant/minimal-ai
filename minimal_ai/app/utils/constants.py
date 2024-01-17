from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel

ICONSET = {
    "data_loader": "ph:cloud",
    "data_transformer": "tabler:transform",
    "data_sink": "material-symbols:download",
}


class ExecutorType(str, Enum):
    """Executor type class"""

    PYTHON = "python"
    PYSPARK = "pyspark"


class PipelineStatus(str, Enum):
    """Pipeline status class"""

    EXECUTED = "executed"
    DRAFT = "draft"
    FAILED = "failed"


class PipelineExecutionStatus(str, Enum):
    """Execution status class"""

    Running = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """Task status class"""

    EXECUTED = "executed"
    FAILED = "failed"
    DRAFT = "draft"
    CONFIGURED = "configured"
    RUNNING = "running"


class PipelineType(str, Enum):
    """Pipeline type to choose between pandas and pyspark"""

    PYTHON = "python"
    PYSPARK = "pyspark"


class TaskType(str, Enum):
    """supported task types"""

    DATA_LOADER = "data_loader"
    DATA_SINK = "data_sink"
    DATA_TRANSFORMER = "data_transformer"


class CronModel(BaseModel):
    """cron model"""

    year: str
    month: str
    day: str
    week: str | None = None
    day_of_week: str | None = None
    hour: str
    minute: str
    second: str


class TaskModel(BaseModel):
    """Model class to define Task"""

    name: str
    task_type: str
    priority: int | None = None
    upstream_task_uuids: List[str] | None = None


class PipelineModel(BaseModel):
    """Model class to define pipeline"""

    name: str
    executor_type: str
    executor_config: Dict[str, str] | None = None
    description: str | None = None


class PipelineUpdateModel(BaseModel):
    """Model class for pipeline update"""

    executor_type: str | None = None
    reactflow_props: Dict[Any, Any] | None = None
    executor_config: Dict[Any, Any] | None = None


class VariableType(str, Enum):
    """Supported variable types"""

    PYTHON_DATAFRAME = "python_dataframe"
    SPARK_DATAFRAME = "spark_dataframe"


class LoaderType(str, Enum):
    """Supported loader type"""

    LOCAL_FILE = "local_file"
    GCP_BUCKET = "gcp_bucket"
    S3_FILE = "s3_file"
    WAREHOUSE = "warehouse"
    BIGQUERY = "bigquery"


class SinkType(str, Enum):
    """Supported sink type"""

    LOCAL_FILE = "local_file"
    MYSQL = "mysql"
    GCP_BUCKET = "gcp_bucket"
    S3_FILE = "s3_file"
    BIGQUERY = "bigquery"


class TransformerType(str, Enum):
    """Supported transformer type"""

    JOIN = "join"
    UNION = "union"
    PIVOT = "pivot"
    FILTER = "filter"
    CUSTOMSQL = "customsql"
    AGGREGATE = "aggregate"


class JoinModel(BaseModel):
    """properties for join type transformer"""

    left_table: str
    right_table: str
    on: str
    how: str
    target_columns: dict[Any, Any]
    where: str | None = None


class AggModel(BaseModel):
    """properties for aggregate type transformer"""

    target_columns: dict[str, str]
    groupby_columns: dict[str, str]


class FilterModel(BaseModel):
    """properties for filter transformer"""

    filter: str


class CustomSql(BaseModel):
    """properties for custom sql"""

    query: str


class PivotModel(BaseModel):
    """properties for pivot transformer"""

    index: List[str]
    columns: List[str]
    values: List[str]


class TaskUpdateModel(BaseModel):
    """properties of task to be updated"""

    upstream_task_uuids: List[str] | None = None
    config_properties: Dict[str, Any] | None = None


class DBConfig(BaseModel):
    """properties for the mysql connection"""

    type: str
    host: str
    port: str
    user: str
    password: str
    database: str
    table: str
    extras: str | None = None
    mode: str | None = None


class FileConfig(BaseModel):
    """properties for file type configurations"""

    type: str
    file_path: str
    extras: str | None = None
    mode: str | None = None


class GSFileConfig(BaseModel):
    """properties for file type configurations"""

    file_type: str
    file_path: str
    mode: str | None = None


class BigQueryConfig(BaseModel):
    """properties for bigquery configurations"""

    table: str
    mode: str | None = None


class ReactflowProps(BaseModel):
    """properties for reactflow"""

    nodes: list[dict]
    edges: list[dict]
    viewport: dict


class TaskColumns(BaseModel):
    """properties to add columns to task"""

    columns: list[str]
