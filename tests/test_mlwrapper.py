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
from ml_wrapper.message_type import MessageType
from ml_wrapper.messaging import IncomingMessage
from ml_wrapper.exceptions import NonSchemaConformJsonPayload, WrongMessageType
from ml_wrapper.json_provider import (
    JSON_ML_ANALYSE_TIME_SERIES,
    JSON_ML_DATA_EXAMPLE,
    JSON_ML_ANALYSE_TEXT,
)
from tests.mock_ml_tools import (
    FFT,
    ResultTypeTool,
    BadMLTool,
    BadTopicTool,
    RequireCertainInput,
)


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
        while fft._async_ready():
            print("Waiting for the tool to finish")
            sleep(1)

    def test_wrong_topic(self):
        btt = BadTopicTool()
        self.assertEqual("this/isnotcorrect", btt._config.get("base_result_topic"))
        self.get_message()
        btt._react_to_message(None, None, self.msg)
        # btt.client.mock_a_message(btt.client, self.msg.payload)
        print(btt.async_result.ready())
        with self.assertLogs("MOCK", level="WARNING") as log:
            while btt._async_ready():
                print("Waiting for the tool to finish")
                sleep(1)
        print("done")
        self.assertTrue(
            any(["undefined topic" in msg and "consider" in msg for msg in log.output])
        )

    def test_require_message_type(self):
        ml_tool = RequireCertainInput()
        ml_tool._only_react_to_message_type = MessageType.SENSOR_UPDATE
        ml_tool.client.mock_a_message(ml_tool.client, json.dumps(JSON_ML_DATA_EXAMPLE))
        ml_tool._only_react_to_message_type = MessageType.ANALYSES_Result
        with self.assertRaises(WrongMessageType):
            ml_tool.client.mock_a_message(
                ml_tool.client, json.dumps(JSON_ML_DATA_EXAMPLE)
            )
        t_series = json.dumps(JSON_ML_ANALYSE_TIME_SERIES)
        text = json.dumps(JSON_ML_ANALYSE_TEXT)
        ml_tool.client.mock_a_message(ml_tool.client, t_series)
        ml_tool._only_react_to_previous_result_types = [
            ResultType.TIME_SERIES,
            ResultType.MULTIPLE_TIME_SERIES,
        ]
        ml_tool.client.mock_a_message(ml_tool.client, t_series)
        with self.assertRaises(WrongMessageType):
            ml_tool.client.mock_a_message(ml_tool.client, text)

    def test_subscription(self):
        ml_tool = FFT()
        subscriptions = list(map(lambda x: x["topic"], ml_tool.client.subscriptions))
        self.assertIn("kosmos/analytics/test_url/test_tag", subscriptions)


if __name__ == "__main__":
    unittest.main()
