"""
This module implements a basic ML Wrapper Mock
"""
# pylint: disable=wrong-import-position
import os
import time
from typing import Union, List
import logging
import pandas as pd


os.environ["CONFIG_MODEL_URL"] = "test"
os.environ["CONFIG_MODEL_TAG"] = "test"
os.environ["CONFIG_MODEL_FROM"] = "test"

from ml_wrapper import MLWrapper
from ml_wrapper.messaging import OutgoingMessage
from ml_wrapper.result_type import ResultType
from ml_wrapper.mock_mqtt_client import MockMqttClient


class FFT(MLWrapper):
    """Mocked FFT class"""

    def __init__(self):
        """Constructor"""
        super().__init__(log_level=logging.DEBUG, logger_name="MOCK")
        self.logger.debug(type(self))
        self.logger.debug(self.config)

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Simple run step"""
        self.logger.debug("Starting run method")
        time.sleep(2)
        dataframe = out_message.in_message.retrieved_data
        dataframe["triple"] = dataframe["time"] * 3
        dataframe["time as text"] = dataframe["time"].astype(str)
        return dataframe


class BadTopicTool(MLWrapper):
    """Mocked FFT class"""

    def __init__(self):
        """Constructor"""
        os.environ["CONFIG_MESSAGING_BASE_RESULT_TOPIC"] = "this/isnotcorrect"
        super().__init__(log_level=logging.DEBUG, logger_name="MOCK")

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Simple run step"""
        self.logger.debug("Starting run method")
        self.logger.warning("I will now calculate my stuff")
        time.sleep(2)
        dataframe = out_message.in_message.retrieved_data
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
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        time.sleep(5)
        return "Done"


class ResultTypeTool(MLWrapper):
    """ Mock for a Result Type Check """

    def __init__(self):
        """ Constructor """
        super().__init__(
            result_type=ResultType.MULTIPLE_TIME_SERIES,
            log_level=logging.DEBUG,
            logger_name="Result Type Logger",
        )

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        return "Done"


class BadMLTool(MLWrapper):
    """ Mock for a corrupt ML Tool """

    def __init__(self):
        """ Constructor """
        super().__init__(logger_name="MOCK", log_level=logging.DEBUG)

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        dataframe = out_message.in_message.retrieved_data
        columns = out_message.in_message.columns
        self.logger.debug(dataframe, columns)
        return "Done"
