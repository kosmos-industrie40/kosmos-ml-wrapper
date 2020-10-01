"""
This module presents an example of a possible ML Tool using the ML Wrapper
"""
# This is only required for testing inside the ML Wrapper package
# pylint: disable=arguments-differ

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
import pandas as pd


# pylint: disable=no-name-in-module
from ml_wrapper import MLWrapper, IncomingMessage, OutgoingMessage, ResultType


# Create child class of MLWrappers
class AnalysisTool(MLWrapper):
    """ My wonderful analysis tool """

    # Implementation required
    def __init__(self):
        # Instantiation of super encouraged to explicitly set the result_type
        super().__init__(result_type=ResultType.TIME_SERIES)

    # Implementation required
    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
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
    def retrieve_payload_data(self, in_message: IncomingMessage) -> IncomingMessage:
        # retrieve data from payload
        # or request historical data from database
        # based on the present information in the payload
        data = pd.DataFrame({"ind": [list(range(10))]})
        in_message.custom_information_field = data
        return in_message


# Usage of AnalysisTool class
if __name__ == "__main__":
    ANALYSIS_TOOL = AnalysisTool()  # instantiate
    ANALYSIS_TOOL.logger.info("Starting my wonderful ml tool")
    ANALYSIS_TOOL.start()  # start infinite loop to listen to MQTT messages
