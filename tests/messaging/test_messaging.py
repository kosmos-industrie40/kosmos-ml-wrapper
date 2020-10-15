"""
Unittests for the Messaging/Information class
"""
import pytest
import pandas as pd


from ml_wrapper import ResultType

from ml_wrapper.exceptions import (
    NotInitialized,
    InvalidTopic,
    NonSchemaConformJsonPayload,
)


def test_uninitialized(new_incoming_message):
    assert not new_incoming_message.is_initialized
    with pytest.raises(NotInitialized):
        new_incoming_message.check_initialized()


@pytest.mark.parametrize(
    "message",
    ["text", "sensor", "sensor_axistest", "time_series", "multiple_time_series"],
)
def test_messaging(new_incoming_message, mqtt_fixtures, message):
    new_incoming_message.mqtt_message = mqtt_fixtures[message]
    print(id(new_incoming_message))
    print(new_incoming_message.__dict__)


@pytest.mark.parametrize(
    "message",
    ["text", "sensor", "sensor_axistest", "time_series", "multiple_time_series"],
)
def test_initialized(new_incoming_message, mqtt_fixtures, message):
    new_incoming_message.mqtt_message = mqtt_fixtures[message]
    assert new_incoming_message.is_initialized
    new_incoming_message.check_initialized()
    print(new_incoming_message.__dict__)


@pytest.mark.parametrize(
    "message",
    ["text", "sensor", "sensor_axistest", "time_series", "multiple_time_series"],
)
def test_retrieve(
    new_incoming_message, mqtt_fixtures, expect_retrieve_fixture, message
):
    new_incoming_message.mqtt_message = mqtt_fixtures[message]
    new_incoming_message.check_retrieved()
    assert (
        new_incoming_message.analyses_message_type
        == expect_retrieve_fixture[message]["result_type"]
    )
    assert isinstance(
        new_incoming_message.retrieved_data, expect_retrieve_fixture[message]["type"]
    )
    print(new_incoming_message.analyses_message_type)
    print(new_incoming_message.retrieved_data)
    if message == "sensor":
        for col in new_incoming_message.columns:
            assert "unit" in new_incoming_message.column_meta[col["name"]]
            assert "description" in new_incoming_message.column_meta[col["name"]]
            assert "future" in new_incoming_message.column_meta[col["name"]]


def test_set_topic(new_incoming_message):
    with pytest.raises(InvalidTopic):
        new_incoming_message.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn"
        new_incoming_message.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn/a/v0"
        new_incoming_message.topic = "/kosmos/nalytics/abce.def-ghi.jkl.omn/a/v0"
        new_incoming_message.topic = "/ksmos/nalytics/abce.def-ghi.jkl.omn/a/v0"
    new_incoming_message.topic = "/kosmos/analytics/abce.def-ghi.jkl.omn/v0"


# pylint: disable=too-many-arguments,too-many-locals
def test_set_body(
    new_incoming_message,
    mqtt_time_series,
    new_outgoing_message_by_incoming_message,
    json_analyse_multiple_time_series,
    json_analyse_text,
    json_analyse_time_series,
    json_data_example,
    json_data_example_2,
    json_data_example_3,
    json_ml_analyse_multiple_time_series,
    json_ml_analyse_text,
    json_ml_analyse_time_series,
    json_ml_data_example,
    json_ml_data_example_2,
    json_ml_data_example_3,
):
    new_incoming_message.mqtt_message = mqtt_time_series
    out = new_outgoing_message_by_incoming_message(new_incoming_message)
    out.body = json_analyse_text["body"]
    out.body = json_analyse_time_series["body"]
    out.body = json_analyse_multiple_time_series["body"]
    with pytest.raises(NonSchemaConformJsonPayload):
        out.body = json_ml_data_example["body"]
        out.body = json_ml_data_example_2["body"]
        out.body = json_ml_data_example_3["body"]
        out.body = json_ml_analyse_text["body"]
        out.body = json_ml_analyse_time_series["body"]
        out.body = json_ml_analyse_multiple_time_series["body"]
        out.body = json_data_example["body"]
        out.body = json_data_example_2["body"]
        out.body = json_data_example_3["body"]


def test_set_results(
    new_incoming_message, new_outgoing_message_by_incoming_message, mqtt_time_series
):
    new_incoming_message.mqtt_message = mqtt_time_series
    out = new_outgoing_message_by_incoming_message(new_incoming_message)
    out.set_results(pd.DataFrame(dict(test=[1, 2, 3])), ResultType.TIME_SERIES)
    with pytest.raises(NonSchemaConformJsonPayload):
        out.set_results(pd.DataFrame())
        out.set_results(pd.DataFrame(), ResultType.TIME_SERIES)
        out.set_results(
            [pd.DataFrame(), pd.DataFrame()], ResultType.MULTIPLE_TIME_SERIES
        )
