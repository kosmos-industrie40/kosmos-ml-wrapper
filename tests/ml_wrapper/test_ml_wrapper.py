"""
Tests the ML Wrapper behaviour
"""
import json
from unittest import mock

import pytest
from ml_wrapper import (
    MessageType,
    MLWrapper,
    NonSchemaConformJsonPayload,
    NotInitialized,
    ResultType,
)


def test_instantiate(ML_MOCK_FFT):
    with ML_MOCK_FFT as ml_mock_fft:
        print(id(ml_mock_fft))
        print(id(ml_mock_fft.async_loop))
        assert isinstance(ml_mock_fft, MLWrapper)


def test_react_to_message(ML_MOCK_FFT, mqtt_time_series):
    with ML_MOCK_FFT as ml_mock_fft:
        print(id(ml_mock_fft))
        print(id(ml_mock_fft.async_loop))
        ml_mock_fft._react_to_message(None, None, mqtt_time_series)


def test_instantiate_2(ML_MOCK_FFT):
    with ML_MOCK_FFT as ml_mock_fft:
        print(id(ml_mock_fft))
        print(id(ml_mock_fft.async_loop))
        assert isinstance(ml_mock_fft, MLWrapper)


def test_react_to_message_2(ML_MOCK_FFT, mqtt_time_series):
    with ML_MOCK_FFT as ml_mock_fft:
        print(id(ml_mock_fft))
        print(id(ml_mock_fft.async_loop))
        ml_mock_fft._react_to_message(None, None, mqtt_time_series)


@pytest.mark.asyncio
async def test_run(ML_MOCK_FFT, mqtt_time_series, new_incoming_message):
    with ML_MOCK_FFT as ml_mock_fft:
        new_incoming_message.mqtt_message = mqtt_time_series
        new_incoming_message_ = await ml_mock_fft.retrieve_payload_data(
            new_incoming_message
        )
        assert new_incoming_message_ == new_incoming_message
        body = await ml_mock_fft._run(new_incoming_message)
        body = body.body_as_json_dict
        assert body["results"] is not None
        assert body["timestamp"] is not None


def test_result_types(ML_MOCK_RESULT_TYPE_TOOL):
    with ML_MOCK_RESULT_TYPE_TOOL as ml_mock_result_type_tool:
        print(id(ml_mock_result_type_tool.async_loop))
        assert ml_mock_result_type_tool.result_type == ResultType.MULTIPLE_TIME_SERIES


@pytest.mark.asyncio
async def test_erroneous_run(
    new_incoming_message, ML_MOCK_BAD_MLTOOL, mqtt_time_series
):
    with ML_MOCK_BAD_MLTOOL as ml_mock_bad_mltool:
        new_incoming_message.mqtt_message = mqtt_time_series
        with pytest.raises(TypeError):
            await ml_mock_bad_mltool._run(new_incoming_message)
        assert len(ml_mock_bad_mltool.out_messages) == 0


def test_reaction_to_message(ML_MOCK_FFT, json_ml_analyse_time_series):
    with ML_MOCK_FFT as ml_mock_fft:
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
        assert len(ml_mock_fft.out_messages) > 0
        assert ml_mock_fft.out_messages[0] is not None
        print(ml_mock_fft.out_messages[0].body)


def test_wrong_topic(ML_MOCK_BAD_TOPIC_TOOL, mqtt_time_series, caplog):
    with ML_MOCK_BAD_TOPIC_TOOL as ml_mock_bad_topic_tool:
        assert (
            ml_mock_bad_topic_tool._config.get("base_result_topic")
            == "this/isnotcorrect"
        )
        ml_mock_bad_topic_tool._react_to_message(None, None, mqtt_time_series)
        assert any(
            ["undefined topic" in msg and "consider" in msg for msg in caplog.messages]
        )


def test_require_message_type(
    ML_MOCK_REQUIRE_CERTAIN_INPUT,
    json_ml_data_example,
    json_ml_analyse_text,
    json_ml_analyse_time_series,
    caplog,
):
    with ML_MOCK_REQUIRE_CERTAIN_INPUT as ml_mock_require_certain_input:
        ml_tool = ml_mock_require_certain_input
        ml_tool._only_react_to_message_type = MessageType.SENSOR_UPDATE
        ml_tool.client.mock_a_message(ml_tool.client, json.dumps(json_ml_data_example))
        ml_tool._only_react_to_message_type = MessageType.ANALYSES_RESULT
        ml_tool.client.mock_a_message(ml_tool.client, json.dumps(json_ml_data_example))
        assert "WrongMessageType" in " ".join(caplog.messages)
        ml_tool.client.mock_a_message(
            ml_tool.client, json.dumps(json_ml_analyse_time_series)
        )
        ml_tool._only_react_to_previous_result_types = [
            ResultType.TIME_SERIES,
            ResultType.MULTIPLE_TIME_SERIES,
        ]
        ml_tool.client.mock_a_message(
            ml_tool.client, json.dumps(json_ml_analyse_time_series)
        )
        ml_tool.client.mock_a_message(ml_tool.client, json.dumps(json_ml_analyse_text))
        assert "WrongMessageType" in " ".join(caplog.messages)


def test_subscription(ML_MOCK_FFT):
    with ML_MOCK_FFT as ml_mock_fft:
        subscriptions = list(
            map(lambda x: x["topic"], ml_mock_fft.client.subscriptions)
        )
        print(subscriptions)
        assert "kosmos/analytics/test_url/test_tag" in subscriptions


@pytest.mark.parametrize("temporary", [True, False])
def test_outgoing_message_is_temporary(
    ML_MOCK_FftMockNOT_INITIALIZED, temporary, json_ml_analyse_time_series
):
    with pytest.raises(AssertionError):
        with ML_MOCK_FftMockNOT_INITIALIZED(outgoing_message_is_temporary=None) as tool:
            pass
    with ML_MOCK_FftMockNOT_INITIALIZED(
        outgoing_message_is_temporary=temporary
    ) as tool:
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_time_series))
        assert all([out.is_temporary for out in tool.out_messages]) == temporary
        assert all(["temporary" in out.topic for out in tool.out_messages]) == temporary


def test_wrong_resolve_function(ML_MOCK_WRONG_RESOLVE, mqtt_time_series, caplog):
    with pytest.raises(NotInitialized):
        with ML_MOCK_WRONG_RESOLVE as ml_tool:
            ml_tool._react_to_message(None, None, mqtt_time_series)
    assert any(
        [
            "You need to specify" in rec.message
            for rec in caplog.records
            if rec.levelname in ["ERROR", "WARNING"]
        ]
    )


def test_additional_field_in_result_of_text_function(
    ML_MOCK_FFT, json_ml_analyse_time_series
):
    async def mock_coroutine(fail=True):
        if fail:
            return {"total": "Fail", "predict": 100, "error": "Hello"}
        return {"total": "Fail", "predict": 100}

    with ML_MOCK_FFT as tool:
        tool.result_type = ResultType.TEXT
        tool.run = mock.Mock(return_value=mock_coroutine(fail=True))
        with pytest.raises(NonSchemaConformJsonPayload):
            tool.client.mock_a_message(
                tool.client, json.dumps(json_ml_analyse_time_series)
            )
        tool.run = mock.Mock(return_value=mock_coroutine(fail=False))
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_time_series))
