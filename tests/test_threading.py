""" This module tests the threading behaviour """
import unittest
import json
import os

from paho.mqtt.client import MQTTMessage

from tests.mock_ml_function import SlowMLTool

JSON_PATH = os.path.join(os.path.dirname(__file__), "../docs/MqttPayloads/")


with open(JSON_PATH + "analyses-example-time_series.json") as f:
    schema = json.load(f)


class TestThreading(unittest.TestCase):
    """ Test Case for threading """

    def test_thread_run(self):
        slowml = SlowMLTool()
        msg = MQTTMessage
        msg.payload = json.dumps(schema)
        self.assertRaises(TypeError, slowml._react_to_message, (None, None, msg))


if __name__ == "__main__":
    unittest.main()
