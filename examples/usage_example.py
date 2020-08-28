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

# This is required for you to write in order to create your own ML Tool
import logging
from typing import Union, List
import pandas as pd
from ml_wrapper import MLWrapper

# This level should be set according to your needs (development, production, ...)
logging.basicConfig(level=logging.DEBUG)


# Create child class of MLWrappers
class AnalysisTool(MLWrapper):
    """ My wonderful analysis tool """

    # Implementation required
    def __init__(self):
        # Instantiation of super required
        super().__init__(log_level=logging.DEBUG)

    # Implementation required
    def run(
        self,
        dataframe: Union[str, pd.DataFrame, None] = None,
        columns: List[dict] = None,
        data: List[dict] = None,
        metadada: Union[List[dict], None] = None,
        timestamp: str = None,
        topic: str = None,
    ) -> Union[str, pd.DataFrame]:
        # perform your ML magic here
        data = pd.DataFrame({"ind": [list(range(10))]})
        return data

    # Implementation Optional
    # Can customize this method to extract desired information from
    # the mqtt payload. Must conform to the args required by the run() method.
    # Default implementation returns
    # dataframe, columns, data, metadada, timestamp
    def retrieve_payload_data(
        self, topic: str, payload: str
    ) -> (Union[pd.DataFrame, None], list, list, Union[dict, list, None], int):
        # retrieve data from payload
        # or request historical data from database
        # based on the present information in the payload
        data = pd.DataFrame({"ind": [list(range(10))]})
        return data


# Usage of AnalysisTool class
if __name__ == "__main__":
    ANALYSIS_TOOL = AnalysisTool()  # instantiate
    ANALYSIS_TOOL.logger.info("Starting my wonderful ml tool")
    ANALYSIS_TOOL.start()  # start infinite loop to listen to MQTT messages
