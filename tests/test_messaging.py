"""
Unittests for the Messaging/Information class
"""
import json
import logging
import unittest
from unittest import TestCase
import pandas as pd

from paho.mqtt.client import MQTTMessage

from src.ml_wrapper import (
    ResultType,
    JSON_ML_ANALYSE_TIME_SERIES,
    JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES,
    JSON_ML_ANALYSE_TEXT,
    JSON_ML_DATA_EXAMPLE,
    JSON_ANALYSE_TEXT,
    JSON_ANALYSE_TIME_SERIES,
    JSON_ANALYSE_MULTIPLE_TIME_SERIES,
    JSON_ML_DATA_EXAMPLE_2,
    JSON_ML_DATA_EXAMPLE_3,
    JSON_DATA_EXAMPLE,
    JSON_DATA_EXAMPLE_2,
    JSON_DATA_EXAMPLE_3,
)
from src.ml_wrapper.exceptions import (
    NotInitialized,
    NonSchemaConformJsonPayload,
    InvalidTopic,
)
from src.ml_wrapper.messaging import IncomingMessage, OutgoingMessage


# pylint: disable=super-init-not-called
class MQTTMessageMock(MQTTMessage):
    """ Mocking Message """

    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload


class TestInformation(TestCase):
    """
    Unittest for the Messaging/Information class
    """

    @classmethod
    def setUpClass(cls) -> None:
        """ Sets up test messages """
        cls.inf_uninitialized = IncomingMessage(logger=logging.getLogger(__file__))
        cls.inf_initialized_analyses_time_series = IncomingMessage(
            logger=logging.getLogger(__file__)
        )
        cls.inf_initialized_analyses_multiple_time_series = IncomingMessage(
            logger=logging.getLogger(__file__)
        )
        cls.inf_initialized_analyses_text = IncomingMessage(
            logger=logging.getLogger(__file__)
        )
        cls.inf_initialized_data = IncomingMessage(logger=logging.getLogger(__file__))
        cls.message_analyses_time_series = MQTTMessageMock(
            b"kosmos/analytics/analyse.test-tool/v0.1.-2",
            json.dumps(JSON_ML_ANALYSE_TIME_SERIES),
        )
        cls.message_analyses_multiple_time_series = MQTTMessageMock(
            b"kosmos/analytics/analyse.test-tool/v0.1.-2",
            json.dumps(JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES),
        )
        cls.message_analyses_text = MQTTMessageMock(
            b"kosmos/analytics/analyse.test-tool/v0.1.-2",
            json.dumps(JSON_ML_ANALYSE_TEXT),
        )
        cls.message_data = MQTTMessageMock(
            b"kosmos/analytics/analyse.test-tool/v0.1.-2",
            json.dumps(JSON_ML_DATA_EXAMPLE),
        )

    def initialize(self):
        """ Initializes messages when required """
        self.inf_initialized_data.mqtt_message = self.message_data
        self.inf_initialized_analyses_time_series.mqtt_message = (
            self.message_analyses_time_series
        )
        self.inf_initialized_analyses_multiple_time_series.mqtt_message = (
            self.message_analyses_multiple_time_series
        )
        self.inf_initialized_analyses_text.mqtt_message = self.message_analyses_text

    def test_messaging(self):
        self.initialize()
        print(self.inf_initialized_data.__dict__)

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
        print(self.inf_initialized_analyses_time_series.analyses_message_type, ":")
        print(self.inf_initialized_analyses_time_series.retrieved_data)

    def test_retrieve_analyse_multiple_time_series(self):
        self.initialize()
        self.inf_initialized_analyses_multiple_time_series.check_retrieved()
        print(
            self.inf_initialized_analyses_multiple_time_series.analyses_message_type,
            ":",
        )
        print(self.inf_initialized_analyses_multiple_time_series.retrieved_data)

    def test_retrieve_analyse_text(self):
        self.initialize()
        self.inf_initialized_analyses_text.check_retrieved()
        print(self.inf_initialized_analyses_text.analyses_message_type, ":")
        print(self.inf_initialized_analyses_text.retrieved_data)

    def test_retrieve_data(self):
        self.initialize()
        self.inf_initialized_data.check_retrieved()
        print(self.inf_initialized_data.analyses_message_type, ":")
        print(self.inf_initialized_data.retrieved_data)

    def test_set_topic(self):
        with self.assertRaises(InvalidTopic):
            self.inf_uninitialized.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn"
            self.inf_uninitialized.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn/a/v0"
            self.inf_uninitialized.topic = "/kosmos/nalytics/abce.def-ghi.jkl.omn/a/v0"
            self.inf_uninitialized.topic = "/ksmos/nalytics/abce.def-ghi.jkl.omn/a/v0"
        self.inf_uninitialized.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn/v0"

    def test_set_payload(self):
        self.initialize()
        out = OutgoingMessage(
            self.inf_initialized_analyses_time_series,
            from_="none",
            model_url="none",
            model_tag="none",
            is_temporary=True,
            temporary_keyword="temporary",
        )
        out.payload = JSON_ANALYSE_TEXT
        out.payload = JSON_ANALYSE_TIME_SERIES
        out.payload = JSON_ANALYSE_MULTIPLE_TIME_SERIES
        with self.assertRaises(NonSchemaConformJsonPayload):
            out.payload = JSON_ML_DATA_EXAMPLE
            out.payload = JSON_ML_DATA_EXAMPLE_2
            out.payload = JSON_ML_DATA_EXAMPLE_3
            out.payload = JSON_ML_ANALYSE_TEXT
            out.payload = JSON_ML_ANALYSE_TIME_SERIES
            out.payload = JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES
            out.payload = JSON_DATA_EXAMPLE
            out.payload = JSON_DATA_EXAMPLE_2
            out.payload = JSON_DATA_EXAMPLE_3

    def test_set_results(self):
        self.initialize()
        out = OutgoingMessage(
            self.inf_initialized_analyses_time_series,
            from_="none",
            model_tag="none",
            model_url="none",
            base_topic="kosmos/analytics",
            is_temporary=True,
            temporary_keyword="temporary",
        )
        out.set_results(pd.DataFrame(dict(test=[1, 2, 3])), ResultType.TIME_SERIES)
        with self.assertRaises(NonSchemaConformJsonPayload):
            out.set_results(pd.DataFrame())
            out.set_results(pd.DataFrame(), ResultType.TIME_SERIES)
            out.set_results(
                [pd.DataFrame(), pd.DataFrame()], ResultType.MULTIPLE_TIME_SERIES
            )


if __name__ == "__main__":
    unittest.main()
