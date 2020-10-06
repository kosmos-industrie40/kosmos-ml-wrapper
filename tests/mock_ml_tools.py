"""
This module implements a basic ML Wrapper Mock
"""
# pylint: disable=wrong-import-position
import os
import time
from typing import Union, List
import logging
import pandas as pd


os.environ["CONFIG_MODEL_URL"] = "test_url"
os.environ["CONFIG_MODEL_TAG"] = "test_tag"
os.environ["CONFIG_MODEL_FROM"] = "test_from"

from src.ml_wrapper import MLWrapper, OutgoingMessage, ResultType
from src.ml_wrapper.mock_mqtt_client import MockMqttClient


class FFT(MLWrapper):
    """Mocked FFT class"""

    def __init__(self, outgoing_message_is_temporary=True):
        """Constructor"""
        self.last_out_message = None
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
            log_level=logging.DEBUG,
            logger_name="MOCK",
        )
        self.logger.debug(type(self))
        self.logger.debug(self.config)

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        out_message = super().resolve_result_data(
            result=result, out_message=out_message
        )
        self.last_out_message = out_message
        return out_message

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

    def __init__(self, outgoing_message_is_temporary=True):
        """Constructor"""
        os.environ["CONFIG_MESSAGING_BASE_RESULT_TOPIC"] = "this/isnotcorrect"
        self.last_out_message = None
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
            log_level=logging.DEBUG,
            logger_name="MOCK",
        )

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        out_message = super().resolve_result_data(
            result=result, out_message=out_message
        )
        self.last_out_message = out_message
        return out_message

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

    def __init__(self, outgoing_message_is_temporary=True):
        """ Constructor """
        self.last_out_message = None
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
        )

    def _init_mqtt(self):
        """ Inits mock Client """
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        out_message = super().resolve_result_data(
            result=result, out_message=out_message
        )
        self.last_out_message = out_message
        return out_message

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        time.sleep(5)
        return "Done"


class ResultTypeTool(MLWrapper):
    """ Mock for a Result Type Check """

    def __init__(self, outgoing_message_is_temporary=True):
        """ Constructor """
        self.last_out_message = None
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
            result_type=ResultType.MULTIPLE_TIME_SERIES,
            log_level=logging.DEBUG,
            logger_name="Result Type Logger",
        )

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        out_message = super().resolve_result_data(
            result=result, out_message=out_message
        )
        self.last_out_message = out_message
        return out_message

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        return "Done"


class BadMLTool(MLWrapper):
    """ Mock for a corrupt ML Tool """

    def __init__(self, outgoing_message_is_temporary=True):
        """ Constructor """
        self.last_out_message = None
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
            logger_name="MOCK",
            log_level=logging.DEBUG,
        )

    def _init_mqtt(self):
        """ Initialise a mock mqtt client """
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        out_message = super().resolve_result_data(
            result=result, out_message=out_message
        )
        self.last_out_message = out_message
        return out_message

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        dataframe = out_message.in_message.retrieved_data
        columns = out_message.in_message.columns
        self.logger.debug(dataframe, columns)
        return "Done"


class RequireCertainInput(MLWrapper):
    """
    Mock for message requirements
    """

    def __init__(self, outgoing_message_is_temporary=True):
        """ Constructor """
        self.last_out_message = None
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
            logger_name="MOCK",
            log_level=logging.DEBUG,
            result_type=ResultType.TEXT,
        )

    def _init_mqtt(self):
        """Initialize a mock mqtt client"""
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        out_message = super().resolve_result_data(
            result=result, out_message=out_message
        )
        self.last_out_message = out_message
        return out_message

    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        self.logger.debug("Do Nothing")
        return {"total": "Done", "predict": 100}
