""" This module tests the threading behaviour """
import unittest
import json

from paho.mqtt.client import MQTTMessage

from tests.mock_ml_tools import SlowMLTool
from ml_wrapper.json_provider import JSON_ML_ANALYSE_TIME_SERIES


class TestThreading(unittest.TestCase):
    """ Test Case for threading """

    def test_thread_run(self):
        slowml = SlowMLTool()
        msg = MQTTMessage
        msg.payload = json.dumps(JSON_ML_ANALYSE_TIME_SERIES)
        self.assertRaises(TypeError, slowml._react_to_message, (None, None, msg))


if __name__ == "__main__":
    unittest.main()
