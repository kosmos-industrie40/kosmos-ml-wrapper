"""
This module implements a basic ML Wrapper Mock
"""
# pylint: disable=wrong-import-position
from typing import Union, List
import logging

import asyncio
import pandas as pd


from ml_wrapper import MLWrapper, OutgoingMessage


class FFT(MLWrapper):
    """Mocked FFT class"""

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Simple run step"""
        self.logger.debug("Starting run method")
        await asyncio.sleep(2)
        dataframe = out_message.in_message.retrieved_data
        dataframe["triple"] = dataframe["time"] * 3
        dataframe["time as text"] = dataframe["time"].astype(str)
        return dataframe


class SimpleTool(MLWrapper):
    """Does Nothing"""

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Simple run step"""
        self.logger.debug("Starting run method")
        await asyncio.sleep(2)
        dataframe = out_message.in_message.retrieved_data
        return dataframe


class BadTopicTool(MLWrapper):
    """Mocked FFT class"""

    def __init__(
        self,
        outgoing_message_is_temporary=True,
        last_out_message: OutgoingMessage = None,
    ):
        """Constructor"""
        self.last_out_message = last_out_message
        super().__init__(
            outgoing_message_is_temporary=outgoing_message_is_temporary,
        )
        self.async_loop = None
        logger = logging.getLogger("MOCK")
        self.logger_ = logger

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Simple run step"""
        self.logger.debug("Starting run method")
        self.logger.warning("I will now calculate my stuff")
        await asyncio.sleep(2)
        dataframe = out_message.in_message.retrieved_data
        dataframe["triple"] = dataframe["time"] * 3
        dataframe["time as text"] = dataframe["time"].astype(str)
        return dataframe


class SlowMLTool(MLWrapper):
    """ Mocking a slow ml tool which sleeps for 5 seconds"""

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        await asyncio.sleep(5)
        return "Done"


class ResultTypeTool(MLWrapper):
    """ Mock for a Result Type Check """

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        return "Done"


class BadMLTool(MLWrapper):
    """ Mock for a corrupt ML Tool """

    async def run(
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

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """Run method implementation"""
        self.logger.debug("Do Nothing")
        return {"total": "Done", "predict": 100}


class WrongResolve(FFT):
    """Minimal wrong resolving"""

    async def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        return out_message
