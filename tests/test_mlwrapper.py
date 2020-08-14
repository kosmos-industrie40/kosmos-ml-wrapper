"""
This module is testing the general ML Wrapper behaviour
"""
import logging
import unittest
import json
import os

from paho.mqtt.client import MQTTMessage
from pandas import DataFrame
from ml_wrapper import MLWrapper, ResultType
from tests.mock_ml_function import FFT, ResultTypeTool, BadMLTool

JSON_PATH = os.path.join(os.path.dirname(__file__), "../docs/MqttPayloads/")

mlw = FFT()
with open(JSON_PATH + "analyses-example-time_series.json") as file:
    analyse_example_payload_ts = json.load(file)

logging.basicConfig(level=logging.DEBUG)


class TestMLWrapper(unittest.TestCase):
    """
    Testcase for the ML Wrapper tests
    """

    def test_instantiate(self):
        self.assertTrue(isinstance(mlw, MLWrapper))

    def test_react_to_message(self):
        msg = MQTTMessage
        msg.payload = json.dumps(analyse_example_payload_ts)
        mlw._react_to_message(None, None, msg)

    def test_run(self):
        data_frame, _, _, _, _ = mlw.retrieve_payload_data(
            json.dumps(analyse_example_payload_ts)
        )
        self.assertIsInstance(data_frame, DataFrame)
        payload = mlw._run(data_frame, None, None, None, None)
        self.assertTrue(payload["results"] is not None)
        self.assertTrue(payload["date"] is not None)

    def test_erroneous_run(self):
        bad_ml = BadMLTool()
        msg = MQTTMessage
        msg.payload = json.dumps(analyse_example_payload_ts)
        self.assertRaises(TypeError, bad_ml._react_to_message, (None, None, msg))

    def test_result_types(self):
        result_type_tool = ResultTypeTool()
        self.assertEqual(result_type_tool.resulttype, ResultType.MULTIPLE_TIME_SERIES)

    def test_reaction_to_message(self):
        fft = FFT()
        jsonify = lambda dict_: str(json.dumps(dict_))
        with self.assertRaises(TypeError):
            fft.client.mock_a_message(fft.client, None)
            fft.client.mock_a_message(fft.client, jsonify({"test": "hi"}))
        fft.client.mock_a_message(fft.client, json.dumps(analyse_example_payload_ts))


if __name__ == "__main__":
    unittest.main()
