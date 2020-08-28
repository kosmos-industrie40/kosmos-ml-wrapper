"""
This module implements a basic ML Wrapper Mock
"""
import time
from typing import Union, List
import logging
import pandas as pd

from ml_wrapper import MLWrapper, ResultType
from ml_wrapper.mock_mqtt_client import MockMqttClient


class FFT(MLWrapper):
    """Mocked FFT class"""

    def __init__(self):
        """Constructor"""
        super().__init__(log_level=logging.INFO, logger_name="Mock FFT")
        self.logger.debug(type(self))
        self.logger.debug(self.config)

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self,
        dataframe: Union[str, pd.DataFrame, None] = None,
        columns: List[dict] = None,
        data: List[dict] = None,
        metadada: Union[List[dict], None] = None,
        timestamp: str = None,
        topic: str = None,
    ) -> Union[str, pd.DataFrame]:
        """Simple run step"""
        self.logger.debug("Starting run method")
        time.sleep(2)
        dataframe["triple"] = dataframe["time"] * 3
        dataframe["time as text"] = dataframe["time"].astype(str)
        return dataframe


class SlowMLTool(MLWrapper):
    """ Mocking a slow ml tool which sleeps for 5 seconds"""

    def __init__(self):
        """ Constructor """
        super().__init__()

    def _init_mqtt(self):
        """ Inits mock Client """
        self.client = MockMqttClient(self.logger)

    def run(
        self,
        dataframe: Union[str, pd.DataFrame, None] = None,
        columns: List[dict] = None,
        data: List[dict] = None,
        metadada: Union[List[dict], None] = None,
        timestamp: str = None,
        topic: str = None,
    ) -> Union[str, pd.DataFrame]:
        """ Run method implementation """
        time.sleep(5)
        return "Done"


class ResultTypeTool(MLWrapper):
    """ Mock for a Result Type Check """

    def __init__(self):
        """ Constructor """
        super().__init__(
            result_type=ResultType.MULTIPLE_TIME_SERIES,
            log_level=logging.INFO,
            logger_name="Result Type Logger",
        )

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self,
        dataframe: Union[str, pd.DataFrame, None] = None,
        columns: List[dict] = None,
        data: List[dict] = None,
        metadada: Union[List[dict], None] = None,
        timestamp: str = None,
        topic: str = None,
    ) -> Union[str, pd.DataFrame]:
        """ Run method implementation """
        return "Done"


class BadMLTool(MLWrapper):
    """ Mock for a corrupt ML Tool """

    def __init__(self):
        """ Constructor """
        super().__init__(log_level=logging.INFO)

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self,
        dataframe: Union[str, pd.DataFrame, None] = None,
        columns: List[dict] = None,
        data: List[dict] = None,
        metadada: Union[List[dict], None] = None,
        timestamp: str = None,
        topic: str = None,
    ) -> Union[str, pd.DataFrame]:
        """ Run method implementation """
        self.logger.debug(dataframe, columns)
        return "Done"
