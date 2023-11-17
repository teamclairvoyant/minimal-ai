import json
import logging
import os
import pickle
from typing import Any, List

import aiofiles
from pydantic.dataclasses import dataclass

from minimal_ai.app.services.minimal_exception import MinimalETLException
from minimal_ai.app.utils.string_utils import clean_name

logger = logging.getLogger(__name__)


@dataclass
class VariableManager:
    variables_dir: str

    @classmethod
    def get_manager(cls, variables_dir: str) -> "VariableManager":
        """
        method to get variable manager object
        Args:
            variables_dir (): path to variables dir of the pipeline

        Returns: object of variable manager

        """
        return VariableManager(variables_dir=variables_dir)

    async def add_variable(
        self, pipeline_uuid: str, task_uuid: str, variable_uuid: str, data: Any
    ) -> None:
        """
        method to add variable and store data
        Args:
            pipeline_uuid (): uuid of the pipeline
            task_uuid (): uuid of the task
            variable_uuid (): uuid of the variable
            data (): dataframe
            data_schema (StructType): type of the variable

        """
        variable = Variable(
            uuid=clean_name(variable_uuid),
            pipeline_uuid=pipeline_uuid,
            task_uuid=task_uuid,
            data=data,
        )
        # Delete data if it exists
        variable.delete(self.variables_dir)

        variable.save(self.variables_dir)

    async def delete_variable(self, variable_uuid: str) -> None:
        """
        method to delete variable
        Args:
            variable_uuid (): uuid of the pipeline

        Returns:

        """
        variable = await Variable.get(self.variables_dir, variable_uuid)

        variable.delete(self.variables_dir)

    async def get_variable_data(self, variable_uuid: str) -> List:
        """
        method to get variable object
        Args:
            variable_uuid (str): uuid of the variable
            sample_count (int): number of rows of the dataframe

        """
        logger.info("Getting sample records task - %s", variable_uuid)
        variable = await Variable.get(self.variables_dir, variable_uuid)

        if not variable:
            logger.error("Variable - %s not loaded properly", variable_uuid)
            raise MinimalETLException(f"Variable - {variable_uuid} not loaded properly")

        return [json.loads(i) for i in variable.data]


class Config:
    arbitrary_types_allowed = True


@dataclass(config=Config)
class Variable:
    uuid: str
    pipeline_uuid: str
    task_uuid: str
    data: Any

    @classmethod
    async def get(cls, variable_dir: str, uuid: str) -> "Variable":
        """
        method to get the saved variable
        Args:
            variable_dir (str): path to variable dir
            uuid (str): uuid of the variable
        Returns:
            Object of type Variable
        """
        variable_path = os.path.join(variable_dir, uuid)
        if not os.path.exists(variable_path):
            logger.error("Variable - %s does not exists", variable_path)
            raise MinimalETLException(f"Variable - {variable_path} does not exist")

        async with aiofiles.open(variable_path, mode="rb") as pickle_file:
            variable = pickle.loads(await pickle_file.read())

        return variable

    def save(self, variable_dir: str):
        """
        method to save variable
        Args:
            variable_dir (): path to variable dir

        """
        if not os.path.exists(variable_dir):
            logger.error("Variable path - %s doesn't exist", variable_dir)
            raise MinimalETLException(f"Variable path - {variable_dir} doesn't exist")

        with open(os.path.join(variable_dir, self.uuid), "wb") as pickle_file:
            pickle.dump(self, pickle_file)

    def delete(self, variable_dir: str):
        """
        method to delete variable file
        Args:
            variable_dir (): path to variable dir

        """
        variable_path = os.path.join(variable_dir, self.uuid)

        if os.path.exists(variable_path):
            logger.info("Deleting variable for pipeline - %s.", self.pipeline_uuid)
            os.remove(variable_path)
