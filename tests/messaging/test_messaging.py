"""
Unittests for the Messaging/Information class
"""

import json
import logging
import pytest
import pandas as pd


from paho.mqtt.client import MQTTMessage

from src.ml_wrapper.exceptions import (
    NotInitialized,
    NonSchemaConformJsonPayload,
    InvalidTopic,
)
from src.ml_wrapper.messaging import IncomingMessage, OutgoingMessage


# def initialize(self):
#     """ Initializes messages when required """
#     self.inf_initialized_data.mqtt_message = self.message_data
#     self.inf_initialized_analyses_time_series.mqtt_message = (
#         self.message_analyses_time_series
#     )
#     self.inf_initialized_analyses_multiple_time_series.mqtt_message = (
#         self.message_analyses_multiple_time_series
#     )
#     self.inf_initialized_analyses_text.mqtt_message = self.message_analyses_text


@pytest.mark.parametrize(
    "message", ["text", "sensor", "time_series", "multiple_time_series"]
)
def test_messaging(new_incoming_message, mqtt_fixtures, message):
    new_incoming_message.mqtt_message = mqtt_fixtures[message]
    print(new_incoming_message.__dict__)


def test_uninitialized(new_incoming_message):
    # assert not new_incoming_message.is_initialized
    print(new_incoming_message.__dict__)
    print(new_incoming_message.is_initialized)
    try:
        new_incoming_message.check_initialized()
    except NotInitialized:
        print("Succeeded")
    pytest.fail("NotInitialized not thrown")


@pytest.mark.parametrize(
    "message", ["text", "sensor", "time_series", "multiple_time_series"]
)
def test_initialized(new_incoming_message, mqtt_fixtures, message):
    new_incoming_message.mqtt_message = mqtt_fixtures[message]
    assert new_incoming_message.is_initialized
    new_incoming_message.check_initialized()
    print(new_incoming_message.__dict__)

# class TestInformation(TestCase):
#     """
#     Unittest for the Messaging/Information class
#     """
#
#
#
#
#     def test_retrieve_analyse_time_series(self):
#         self.initialize()
#         self.inf_initialized_analyses_time_series.check_retrieved()
#         print(self.inf_initialized_analyses_time_series.analyses_message_type, ":")
#         print(self.inf_initialized_analyses_time_series.retrieved_data)
#
#     def test_retrieve_analyse_multiple_time_series(self):
#         self.initialize()
#         self.inf_initialized_analyses_multiple_time_series.check_retrieved()
#         print(
#             self.inf_initialized_analyses_multiple_time_series.analyses_message_type,
#             ":",
#         )
#         print(self.inf_initialized_analyses_multiple_time_series.retrieved_data)
#
#     def test_retrieve_analyse_text(self):
#         self.initialize()
#         self.inf_initialized_analyses_text.check_retrieved()
#         print(self.inf_initialized_analyses_text.analyses_message_type, ":")
#         print(self.inf_initialized_analyses_text.retrieved_data)
#
#     def test_retrieve_data(self):
#         self.initialize()
#         self.inf_initialized_data.check_retrieved()
#         print(self.inf_initialized_data.analyses_message_type, ":")
#         print(self.inf_initialized_data.retrieved_data)
#         self.assertIn(
#             "unit",
#             self.inf_initialized_data.column_meta[
#                 self.inf_initialized_data.columns[0]["name"]
#             ],
#         )
#         print(self.inf_initialized_data.column_meta)
#
#     def test_set_topic(self):
#         with self.assertRaises(InvalidTopic):
#             self.inf_uninitialized.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn"
#             self.inf_uninitialized.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn/a/v0"
#             self.inf_uninitialized.topic = "/kosmos/nalytics/abce.def-ghi.jkl.omn/a/v0"
#             self.inf_uninitialized.topic = "/ksmos/nalytics/abce.def-ghi.jkl.omn/a/v0"
#         self.inf_uninitialized.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn/v0"
#
#     def test_set_body(self):
#         self.initialize()
#         out = OutgoingMessage(
#             self.inf_initialized_analyses_time_series,
#             from_="none",
#             model_url="none",
#             model_tag="none",
#             is_temporary=True,
#             temporary_keyword="temporary",
#         )
#         out.body = JSON_ANALYSE_TEXT["body"]
#         out.body = JSON_ANALYSE_TIME_SERIES["body"]
#         out.body = JSON_ANALYSE_MULTIPLE_TIME_SERIES["body"]
#         with self.assertRaises(NonSchemaConformJsonPayload):
#             out.body = JSON_ML_DATA_EXAMPLE["body"]
#             out.body = JSON_ML_DATA_EXAMPLE_2["body"]
#             out.body = JSON_ML_DATA_EXAMPLE_3["body"]
#             out.body = JSON_ML_ANALYSE_TEXT["body"]
#             out.body = JSON_ML_ANALYSE_TIME_SERIES["body"]
#             out.body = JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES["body"]
#             out.body = JSON_DATA_EXAMPLE["body"]
#             out.body = JSON_DATA_EXAMPLE_2["body"]
#             out.body = JSON_DATA_EXAMPLE_3["body"]
#
#     def test_set_results(self):
#         self.initialize()
#         out = OutgoingMessage(
#             self.inf_initialized_analyses_time_series,
#             from_="none",
#             model_tag="none",
#             model_url="none",
#             base_topic="kosmos/analytics",
#             is_temporary=True,
#             temporary_keyword="temporary",
#         )
#         out.set_results(pd.DataFrame(dict(test=[1, 2, 3])), ResultType.TIME_SERIES)
#         with self.assertRaises(NonSchemaConformJsonPayload):
#             out.set_results(pd.DataFrame())
#             out.set_results(pd.DataFrame(), ResultType.TIME_SERIES)
#             out.set_results(
#                 [pd.DataFrame(), pd.DataFrame()], ResultType.MULTIPLE_TIME_SERIES
#             )
#
#
# if __name__ == "__main__":
#     unittest.main()
