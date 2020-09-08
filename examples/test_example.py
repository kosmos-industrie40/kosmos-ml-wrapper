"""
This module presents an example of a possible ML Tool Unittest using the ML Wrapper
"""
# This is only required for testing inside the ML Wrapper package
# pylint: disable=redefined-builtin,wrong-import-position
# pylint: disable=duplicate-code,useless-super-delegation
import json

if __name__ == "__main__" and __package__ is None:
    from sys import path as pth
    from os.path import dirname

    pth.append(dirname(pth[0]))
    __package__ = "examples"

# This is required for you to write in order to create your own ML Tool

import unittest
from examples.usage_example import AnalysisTool
from ml_wrapper.mock_mqtt_client import MockMqttClient
from ml_wrapper.json_provider import JSON_ML_ANALYSE_TIME_SERIES

# Just make a local Mock Class of your own ml tool and copy paste the rest of this class
class MockAnalysisTool(AnalysisTool):
    """ The mock child of your Analysis Tool """

    def __init__(self):
        """ Constructor """
        super().__init__()

    def _init_mqtt(self):
        """ Mock the mqtt client on init """
        self.client = MockMqttClient(self.logger)


# You can now write all your test cases and by calling the mock_a_message function of your Mock
# class, you emulate an incoming message
# pylint: disable=missing-function-docstring,no-self-use
class TestMyMLLogic(unittest.TestCase):
    """ Testcase for your ml tool """

    def test_my_ml_logic(self):
        mock = MockAnalysisTool()
        mock.client.mock_a_message(mock.client, json.dumps(JSON_ML_ANALYSE_TIME_SERIES))
