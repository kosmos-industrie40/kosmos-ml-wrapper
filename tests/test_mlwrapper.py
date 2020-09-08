"""
This module is testing the general ML Wrapper behaviour
"""
# pylint: disable=wrong-import-position
import os
import unittest
import json
from time import sleep

from paho.mqtt.client import MQTTMessage

os.environ["CONFIG_LOGGING_LOG_LEVEL"] = "DEBUG"

from ml_wrapper.ml_wrapper import MLWrapper
from ml_wrapper.result_type import ResultType
from ml_wrapper.messaging import IncomingMessage
from ml_wrapper.exceptions import NonSchemaConformJsonPayload
from ml_wrapper.json_provider import JSON_ML_ANALYSE_TIME_SERIES
from tests.mock_ml_tools import FFT, ResultTypeTool, BadMLTool, BadTopicTool


class TestMLWrapper(unittest.TestCase):
    """
    Testcase for the ML Wrapper tests
    """

    # pylint: disable=attribute-defined-outside-init
    def get_mltool(self):
        self.mlw = FFT()

    # pylint: disable=attribute-defined-outside-init
    def get_message(self):
        msg = MQTTMessage
        msg.topic = "kosmos/analytics/model/tag"
        msg.payload = json.dumps(JSON_ML_ANALYSE_TIME_SERIES)
        self.msg = msg

    def test_instantiate(self):
        self.get_mltool()
        self.assertTrue(isinstance(self.mlw, MLWrapper))

    def test_react_to_message(self):
        self.get_message()
        self.get_mltool()
        self.mlw._react_to_message(None, None, self.msg)

    def test_run(self):
        self.get_mltool()
        self.get_message()
        in_message = IncomingMessage(self.mlw.logger)
        in_message.mqtt_message = self.msg
        in_message_new = self.mlw.retrieve_payload_data(in_message)
        self.assertEqual(in_message_new, in_message)
        payload = self.mlw._run(in_message).payload_as_json_dict
        self.assertIsNotNone(payload["results"])
        self.assertIsNotNone(payload["timestamp"])

    def test_erroneous_run(self):
        bad_ml = BadMLTool()
        self.get_message()
        self.assertRaises(TypeError, bad_ml._react_to_message, (None, None, self.msg))

    def test_result_types(self):
        result_type_tool = ResultTypeTool()
        self.assertEqual(result_type_tool.result_type, ResultType.MULTIPLE_TIME_SERIES)

    def test_reaction_to_message(self):
        fft = FFT()
        with self.assertRaises(TypeError):
            fft.client.mock_a_message(fft.client, None)
        with self.assertRaises(KeyError):
            fft.client.mock_a_message(fft.client, str(json.dumps({"test": "hi"})))
        with self.assertRaises(NonSchemaConformJsonPayload):
            fft.client.mock_a_message(
                fft.client, str(json.dumps({"type": "text", "test": "hi"}))
            )
        fft.client.mock_a_message(fft.client, json.dumps(JSON_ML_ANALYSE_TIME_SERIES))

    def test_wrong_topic(self):
        btt = BadTopicTool()
        self.get_message()
        btt._react_to_message(None, None, self.msg)
        while btt.async_result is None:
            sleep(1)


if __name__ == "__main__":
    unittest.main()
