"""
Unittests for the Messaging/Information class
"""
from os.path import dirname, join, abspath
from unittest import TestCase

from paho.mqtt.client import MQTTMessage

from ml_wrapper.exceptions import NotInitialized
from ml_wrapper.messaging import IncomingMessage


FILE_DIR = dirname(abspath(__file__))

SCHEMA_DIR = abspath(join(FILE_DIR, "..", "docs", "MqttPayloads"))

with open(join(SCHEMA_DIR, "analyses-example-time_series.json")) as file:
    ANALYSES_EXAMPLE_TIME_SERIES = file.read()

with open(join(SCHEMA_DIR, "analyses-example-multiple_time_series.json")) as file:
    ANALYSES_EXAMPLE_MULTIPLE_TIME_SERIES = file.read()

with open(join(SCHEMA_DIR, "analyses-example-text.json")) as file:
    ANALYSES_EXAMPLE_TEXT = file.read()

with open(join(SCHEMA_DIR, "data-example-3.json")) as file:
    DATA_EXAMPLE = file.read()


class MQTTMessageMock(MQTTMessage):
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload


class TestInformation(TestCase):
    """
    Unittest for the Messaging/Information class
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.inf_uninitialized = IncomingMessage()
        cls.inf_initialized_analyses_time_series = IncomingMessage()
        cls.inf_initialized_analyses_multiple_time_series = IncomingMessage()
        cls.inf_initialized_analyses_text = IncomingMessage()
        cls.inf_initialized_data = IncomingMessage()
        cls.message_analyses_time_series = MQTTMessageMock(
            b"kosmos/analyses/<ContractId>", ANALYSES_EXAMPLE_TIME_SERIES
        )
        cls.message_analyses_multiple_time_series = MQTTMessageMock(
            b"kosmos/analyses/<ContractId>", ANALYSES_EXAMPLE_MULTIPLE_TIME_SERIES
        )
        cls.message_analyses_text = MQTTMessageMock(
            b"kosmos/analyses/<ContractId>", ANALYSES_EXAMPLE_TEXT
        )
        cls.message_data = MQTTMessageMock(
            b"kosmos/machine-data/<machineID>/sensor/<sensorID>/update", DATA_EXAMPLE
        )

    def initialize(self):
        self.inf_initialized_data.mqtt_message = self.message_data
        self.inf_initialized_analyses_time_series.mqtt_message = (
            self.message_analyses_time_series
        )
        self.inf_initialized_analyses_multiple_time_series.mqtt_message = (
            self.message_analyses_multiple_time_series
        )
        self.inf_initialized_analyses_text.mqtt_message = self.message_analyses_text

    def test_initialized(self):
        self.assertEqual(self.inf_uninitialized.is_initialized, False)
        self.assertRaises(NotInitialized, self.inf_uninitialized.check_initialized)
        self.initialize()
        self.assertEqual(self.inf_initialized_analyses_time_series.is_initialized, True)
        self.assertEqual(self.inf_initialized_data.is_initialized, True)
        try:
            self.inf_initialized_analyses_time_series.check_initialized()
            self.inf_initialized_data.check_initialized()
        except NotInitialized:
            self.fail(
                "check_initialized on initialized information object "
                "raises NotInitialized although it should not"
            )
        print(self.inf_initialized_data.__dict__)
        print(self.inf_initialized_analyses_time_series.__dict__)

    def test_retrieve_analyse_time_series(self):
        self.initialize()
        self.inf_initialized_analyses_time_series.check_retrieved()
        print(self.inf_initialized_analyses_time_series.message_data_type, ":")
        print(self.inf_initialized_analyses_time_series.retrieved_data)

    def test_retrieve_analyse_multiple_time_series(self):
        self.initialize()
        self.inf_initialized_analyses_multiple_time_series.check_retrieved()
        print(self.inf_initialized_analyses_multiple_time_series.message_data_type, ":")
        print(self.inf_initialized_analyses_multiple_time_series.retrieved_data)

    def test_retrieve_analyse_text(self):
        self.initialize()
        self.inf_initialized_analyses_text.check_retrieved()
        print(self.inf_initialized_analyses_text.message_data_type, ":")
        print(self.inf_initialized_analyses_text.retrieved_data)

    def test_retrieve_data(self):
        self.initialize()
        self.inf_initialized_data.check_retrieved()
        print(self.inf_initialized_data.message_data_type, ":")
        print(self.inf_initialized_data.retrieved_data)
