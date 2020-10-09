"""
Tests the ML Wrapper behaviour
"""
from time import sleep
from typing import List
import json

import pytest
import pandas as pd
from ml_wrapper import (
    MLWrapper,
    ResultType,
    NonSchemaConformJsonPayload,
    MessageType,
    Union,
    OutgoingMessage,
)

from tests.mock_ml_tools import FFT


def test_instantiate(ml_mock_fft):
    assert isinstance(ml_mock_fft, MLWrapper)


def test_react_to_message(ml_mock_fft, mqtt_time_series):
    ml_mock_fft._react_to_message(None, None, mqtt_time_series)


def test_run(ml_mock_fft, mqtt_time_series, new_incoming_message):
    new_incoming_message.mqtt_message = mqtt_time_series
    new_incoming_message_ = ml_mock_fft.retrieve_payload_data(new_incoming_message)
    assert new_incoming_message_ == new_incoming_message
    body = ml_mock_fft._run(new_incoming_message).body_as_json_dict
    assert body["results"] is not None
    assert body["timestamp"] is not None


def test_result_types(ml_mock_result_type_tool):
    assert ml_mock_result_type_tool.result_type == ResultType.MULTIPLE_TIME_SERIES


def test_erroneous_run(new_incoming_message, ml_mock_bad_mltool, mqtt_time_series):
    new_incoming_message.mqtt_message = mqtt_time_series
    with pytest.raises(TypeError):
        ml_mock_bad_mltool._run(new_incoming_message)
    assert ml_mock_bad_mltool.last_out_message is None


def test_reaction_to_message(ml_mock_fft, json_ml_analyse_time_series):
    with pytest.raises(TypeError):
        ml_mock_fft.client.mock_a_message(ml_mock_fft.client, None)
    with pytest.raises(KeyError):
        ml_mock_fft.client.mock_a_message(
            ml_mock_fft.client, str(json.dumps({"test": "hi"}))
        )
    with pytest.raises(NonSchemaConformJsonPayload):
        ml_mock_fft.client.mock_a_message(
            ml_mock_fft.client,
            str(json.dumps({"body": {"type": "text", "test": "hi"}})),
        )
    ml_mock_fft.client.mock_a_message(
        ml_mock_fft.client, json.dumps(json_ml_analyse_time_series)
    )
    while ml_mock_fft.async_not_ready():
        print("Waiting for tool to finish")
        sleep(1)
    assert ml_mock_fft.last_out_message is not None
    print(ml_mock_fft.last_out_message.body)


def test_wrong_topic(ml_mock_bad_topic_tool, mqtt_time_series, caplog):
    assert (
        ml_mock_bad_topic_tool._config.get("base_result_topic") == "this/isnotcorrect"
    )
    ml_mock_bad_topic_tool._react_to_message(None, None, mqtt_time_series)
    while ml_mock_bad_topic_tool.async_not_ready():
        sleep(1)
    assert any(
        ["undefined topic" in msg and "consider" in msg for msg in caplog.messages]
    )


def test_require_message_type(
    ml_mock_require_certain_input,
    json_ml_data_example,
    json_ml_analyse_text,
    json_ml_analyse_time_series,
    caplog,
):
    ml_tool = ml_mock_require_certain_input
    ml_tool._only_react_to_message_type = MessageType.SENSOR_UPDATE
    ml_tool.client.mock_a_message(ml_tool.client, json.dumps(json_ml_data_example))
    ml_tool._only_react_to_message_type = MessageType.ANALYSES_Result
    ml_tool.client.mock_a_message(ml_tool.client, json.dumps(json_ml_data_example))
    assert "WrongMessageType" in " ".join(caplog.messages)
    ml_tool.client.mock_a_message(
        ml_tool.client, json.dumps(json_ml_analyse_time_series)
    )
    while ml_tool.async_result is not None and not ml_tool.async_result.ready():
        sleep(1)
    ml_tool._only_react_to_previous_result_types = [
        ResultType.TIME_SERIES,
        ResultType.MULTIPLE_TIME_SERIES,
    ]
    ml_tool.client.mock_a_message(
        ml_tool.client, json.dumps(json_ml_analyse_time_series)
    )
    # with self.assertLogs("MOCK", level="ERROR") as log2:
    ml_tool.client.mock_a_message(ml_tool.client, json.dumps(json_ml_analyse_text))
    assert "WrongMessageType" in " ".join(caplog.messages)


def test_subscription(ml_mock_fft):
    subscriptions = list(map(lambda x: x["topic"], ml_mock_fft.client.subscriptions))
    assert "kosmos/analytics/test_url/test_tag" in subscriptions


@pytest.mark.parametrize("temporary", [True, False])
def test_outgoing_message_is_temporary(
    ml_mock_fft, temporary, json_ml_analyse_time_series
):
    with pytest.raises(AssertionError):
        type(ml_mock_fft)(outgoing_message_is_temporary=None)
    fft = type(ml_mock_fft)(outgoing_message_is_temporary=temporary)
    fft.client.mock_a_message(fft.client, json.dumps(json_ml_analyse_time_series))
    while fft.async_not_ready():
        sleep(1)
    assert fft.last_out_message.is_temporary == temporary
    assert ("temporary" in fft.last_out_message.topic) == temporary


def test_wrong_resolve_function(mqtt_time_series, caplog):
    class WrongResolve(FFT):
        """Minimal wrong resolving"""

        def resolve_result_data(
            self,
            result: Union[pd.DataFrame, List[pd.DataFrame], dict],
            out_message: OutgoingMessage,
        ) -> OutgoingMessage:
            return out_message

    ml_tool = WrongResolve()
    ml_tool._react_to_message(None, None, mqtt_time_series)
    while ml_tool.async_not_ready():
        sleep(1)
    assert any(
        [
            "You need to specify" in rec.message
            for rec in caplog.records
            if rec.levelname in ["ERROR", "WARNING"]
        ]
    )
