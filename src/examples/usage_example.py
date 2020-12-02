"""
This module presents an example of a possible ML Tool using the ML Wrapper
"""
# This is only required for testing inside the ML Wrapper package
# pylint: disable=redefined-builtin,wrong-import-position,duplicate-code
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir

    path.append(dir(path[0]))
    __package__ = "examples"

import os

os.environ["CONFIG_MODEL_URL"] = "test"
os.environ["CONFIG_MODEL_TAG"] = "test"
os.environ["CONFIG_MODEL_FROM"] = "test"
os.environ["CONFIG_LOGGING_LOG_LEVEL"] = "DEBUG"

# This is required for you to write in order to create your own ML Tool

from typing import Union, List
import asyncio  # pylint: disable=unused-import
import pandas as pd


from ml_wrapper import MLWrapper, IncomingMessage, OutgoingMessage, ResultType

# Create child class of MLWrappers
class AnalysisTool(MLWrapper):
    """ My wonderful analysis tool """

    # Implementation required => Specifies variables required in the ML Wrapper class
    def __init__(self):
        # Instantiation of super encouraged to explicitly set the result_type and whether your data
        # needs to be stored
        super().__init__(
            result_type=ResultType.TIME_SERIES, outgoing_message_is_temporary=False
        )

    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """ This is the main logic routine executed by the ML Wrapper """
        # perform your ML magic here
        self.logger.info(
            "Here you can find the seperately retrieved information. Just call "
            "out_message.in_message.custom_information_field"
        )
        self.logger.info("\n%s", out_message.in_message.custom_information_field)
        data = pd.DataFrame({"ind": [list(range(10))]})
        return data

    # Implementation Optional
    # Can customize this method to extract desired information from
    # the mqtt payload. Must conform to the args required by the run() method.
    # Default implementation returns
    # dataframe, columns, data, metadada, timestamp
    async def retrieve_payload_data(
        self, in_message: IncomingMessage
    ) -> IncomingMessage:
        """ This will be executed before the run method """
        # retrieve data from payload
        # or request historical data from database
        # based on the present information in the payload
        data = pd.DataFrame({"ind": [list(range(10))]})
        in_message.custom_information_field = data
        return in_message


# Usage of AnalysisTool class
if __name__ == "__main__":
    with AnalysisTool() as tool:
        tool.logger.info("Start the tool")
