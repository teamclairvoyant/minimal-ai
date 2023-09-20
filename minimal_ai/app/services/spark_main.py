import json
import logging
from os import environ, listdir, path
from typing import Any, Dict

import __main__
from pydantic.dataclasses import dataclass
from pyspark import SparkFiles
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


@dataclass
class SparkMain:
    """
    Class containing method to start the Spark Session.
    """
    app_name: str
    config: Dict

    def start_spark(self, master='local[*]', jar_packages=[],
                    files=[], spark_config={}) -> Any:
        """Start Spark session, get Spark logger and load config files.
        Start a Spark session on the worker node and register the Spark
        application with the cluster. Note, that only the app_name argument
        will apply when this is called from a script sent to spark-submit.
        All other arguments exist solely for testing the script from within
        an interactive Python console.

        This function also looks for a file ending in 'config.json' that
        can be sent with the Spark job. If it is found, it is opened,
        the contents parsed (assuming it contains valid JSON for the ETL job
        configuration) into a dict of ETL job configuration parameters,
        which are returned as the last element in the tuple returned by
        this function. If the file cannot be found then the return tuple
        only contains the Spark session and Spark logger objects and None
        for config.

        The function checks the enclosing environment to see if it is being
        run from inside an interactive console session or from an
        environment which has a `DEBUG` environment variable set (e.g.
        setting `DEBUG=1` as an environment variable as part of a debug
        configuration within an IDE such as Visual Studio Code or PyCharm.
        In this scenario, the function uses all available function arguments
        to start a PySpark driver from the local PySpark package as opposed
        to using the spark-submit and Spark cluster defaults. This will also
        use local module imports, as opposed to those in the zip archive
        sent to spark via the --py-files flag in spark-submit.

        :param master: Cluster connection details (defaults to local[*]).
        :param jar_packages: List of Spark JAR package names.
        :param files: List of files to send to Spark cluster (master and
            workers).
        :param spark_config: Dictionary of config key-value pairs.
        :return: A tuple of references to the Spark session, logger and
            config dict (only if available).
        """

        # detect execution environment
        flag_repl = not hasattr(__main__, '__file__')
        flag_debug = 'DEBUG' in environ
        logger.info(
            "Starting spark session -> %s", self.app_name)
        if not (flag_repl or flag_debug):
            # get Spark session factory
            spark_builder = (
                SparkSession
                .builder
                .appName(self.app_name))  # type: ignore
        else:
            # get Spark session factory
            spark_builder = (
                SparkSession
                .builder
                .master(master)  # type: ignore
                .appName(self.app_name))

            # create Spark JAR packages string
            spark_jars_packages = ','.join(list(jar_packages))
            spark_builder.config('spark.jars.packages', spark_jars_packages)
            # spark_builder.config('spark.driver.bindAddress', "127.0.0.1")

            spark_files = ','.join(list(files))
            spark_builder.config('spark.files', spark_files)

            # add other config params
            for key, val in spark_config.items():
                spark_builder.config(key, val)

        # create session and retrieve Spark logger object
        spark_sess = spark_builder.getOrCreate()

        # get config file if sent to cluster with --files
        spark_files_dir = SparkFiles.getRootDirectory()
        config_files = [filename
                        for filename in listdir(spark_files_dir)
                        if filename.endswith('config.json')]

        if config_files:
            path_to_config_file = path.join(spark_files_dir, config_files[0])
            with open(path_to_config_file, 'r') as config_file:
                config_dict = json.load(config_file)
            logger.info('loaded config from - %s', config_files[0])
        else:
            logger.info('no extra config file were provided')
            config_dict = None

        return spark_sess, config_dict
