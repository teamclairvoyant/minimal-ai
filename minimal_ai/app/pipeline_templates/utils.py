import logging
import os
import shutil

import jinja2

logger = logging.getLogger(__name__)

template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    lstrip_blocks=True,
    trim_blocks=True,
)


def copy_template(source_dir: str, target_dir: str) -> None:
    """Method to copy template from source to directory

    Args:
        source_dir (str): source path
        target_dir (str): destination path
    """
    template_path = os.path.join(os.path.dirname(__file__), source_dir)
    if not os.path.exists(template_path):
        raise IOError(f"Template folder does not exists - {template_path}")

    shutil.copytree(template_path, target_dir)


def fetch_template(template_path: str) -> jinja2.Template:
    """method to fetch the template code

    Args:
        template_path (str): path to tamplate file

    Returns:
        jinja2.Template: _description_
    """
    return template_env.get_template(template_path)


def generate_pipeline_graph(tasks: dict) -> str:
    """metod to generte code for pipeline execution graph

    Args:
        tasks (dict): tasks defined in the pipeline

    Returns:
        str: generated code
    """
    return "\n".join(
        [
            f"""    df_{tasks[task]["uuid"]} = {tasks[task]["uuid"]}(spark{", " + ", ".join([f"df_{upstream_task}" for upstream_task in tasks[task]["upstream_tasks"]])  if tasks[task]["upstream_tasks"] else ""})"""
            if tasks[task]["task_type"] != "data_sink"
            else f"""    {tasks[task]["uuid"]}(spark{", df_" + tasks[task]["upstream_tasks"][0] if tasks[task]["upstream_tasks"] else ""})"""
            for task in tasks
        ]
    )


def generate_tasks_import(tasks: list) -> str:
    """metod to generte code for tasks import

    Args:
        tasks (dict): tasks defined in the pipeline

    Returns:
        str: generated code
    """
    return "\n".join([f"from .{task} import {task}" for task in tasks])
