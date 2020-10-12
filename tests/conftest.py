"""
Basic conftest file for root level.
Providing jsons, (mqtt) messages and ml tools as fixtures
"""
import inspect
import json
import logging

import pytest
from paho.mqtt.client import MQTTMessage

from ml_wrapper import IncomingMessage, MLWrapper, ResultType
from ml_wrapper.mocks import create_mock_tool
from ml_wrapper.json_provider import (
    JSON_ANALYSE_MULTIPLE_TIME_SERIES,
    JSON_ANALYSE_TEXT,
    JSON_ANALYSE_TIME_SERIES,
    JSON_DATA_EXAMPLE,
    JSON_DATA_EXAMPLE_2,
    JSON_DATA_EXAMPLE_3,
    JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES,
    JSON_ML_ANALYSE_TEXT,
    JSON_ML_ANALYSE_TIME_SERIES,
    JSON_ML_DATA_EXAMPLE,
    JSON_ML_DATA_EXAMPLE_2,
    JSON_ML_DATA_EXAMPLE_3,
)

from tests.mock_ml_tools import (
    FFT,
    BadTopicTool,
    SlowMLTool,
    ResultTypeTool,
    BadMLTool,
    RequireCertainInput,
    WrongResolve,
)

FftMock = create_mock_tool(FFT)
ToolMock = create_mock_tool(WrongResolve)
BttMock = create_mock_tool(BadTopicTool)
SlowMlToolMock = create_mock_tool(SlowMLTool)
ResultTypeToolMock = create_mock_tool(ResultTypeTool)
BadMlToolMock = create_mock_tool(BadMLTool)
RequireCertainInputMock = create_mock_tool(RequireCertainInput)


def _copy(dict_):
    return json.loads(json.dumps(dict_))


@pytest.fixture
def split_topics():
    return ["a/b/c", "a/bc", "abc/t"]


@pytest.fixture
def json_data_example():
    return _copy(JSON_DATA_EXAMPLE)


@pytest.fixture
def json_data_example_2():
    return _copy(JSON_DATA_EXAMPLE_2)


@pytest.fixture
def json_data_example_3():
    return _copy(JSON_DATA_EXAMPLE_3)


@pytest.fixture
def json_analyse_text():
    return _copy(JSON_ANALYSE_TEXT)


@pytest.fixture
def json_analyse_time_series():
    return _copy(JSON_ANALYSE_TIME_SERIES)


@pytest.fixture
def json_analyse_multiple_time_series():
    return _copy(JSON_ANALYSE_MULTIPLE_TIME_SERIES)


@pytest.fixture
def json_ml_analyse_text():
    return _copy(JSON_ML_ANALYSE_TEXT)


@pytest.fixture
def json_ml_analyse_multiple_time_series():
    return _copy(JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES)


@pytest.fixture
def json_ml_analyse_time_series():
    return _copy(JSON_ML_ANALYSE_TIME_SERIES)


@pytest.fixture
def json_ml_data_example():
    return _copy(JSON_ML_DATA_EXAMPLE)


@pytest.fixture
def json_ml_data_example_2():
    return _copy(JSON_ML_DATA_EXAMPLE_2)


@pytest.fixture
def json_ml_data_example_3():
    return _copy(JSON_ML_DATA_EXAMPLE_3)


@pytest.fixture
def tool_patch(monkeypatch):
    monkeypatch.setenv("CONFIG_MODEL_URL", "test_url")
    monkeypatch.setenv("CONFIG_MODEL_TAG", "test_tag")
    monkeypatch.setenv("CONFIG_MODEL_FROM", "test_from")


@pytest.fixture
def ML_MOCK_FFT(tool_patch) -> MLWrapper:
    print(inspect.getsource(FftMock.__init__))
    return FftMock(outgoing_message_is_temporary=True)


@pytest.fixture
def ML_MOCK_FftMockNOT_INITIALIZED(tool_patch) -> MLWrapper:
    print(inspect.getsource(FftMock.__init__))
    return FftMock


@pytest.fixture
def ML_MOCK_WRONG_RESOLVE(tool_patch) -> MLWrapper:
    return ToolMock(outgoing_message_is_temporary=True)


@pytest.fixture
def ML_MOCK_BAD_TOPIC_TOOL(tool_patch, monkeypatch) -> MLWrapper:
    monkeypatch.setenv("CONFIG_MESSAGING_BASE_RESULT_TOPIC", "this/isnotcorrect")
    return BttMock(outgoing_message_is_temporary=True)


@pytest.fixture
def ML_MOCK_SLOW_MLTOOL(tool_patch) -> MLWrapper:
    return SlowMlToolMock(outgoing_message_is_temporary=True)


@pytest.fixture
def ML_MOCK_RESULT_TYPE_TOOL(tool_patch) -> MLWrapper:
    return ResultTypeToolMock(
        outgoing_message_is_temporary=True, result_type=ResultType.MULTIPLE_TIME_SERIES
    )


@pytest.fixture
def ML_MOCK_BAD_MLTOOL(tool_patch) -> MLWrapper:
    return BadMlToolMock(outgoing_message_is_temporary=True)


@pytest.fixture
def ML_MOCK_REQUIRE_CERTAIN_INPUT(tool_patch) -> MLWrapper:
    return RequireCertainInputMock(
        outgoing_message_is_temporary=True, result_type=ResultType.TEXT
    )


@pytest.fixture
def new_incoming_message():
    return IncomingMessage(logger=logging.getLogger(__file__))


# pylint: disable=super-init-not-called
class MQTTMessageMock(MQTTMessage):
    """ Mocking Message """

    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload


@pytest.fixture
def mqtt_time_series(json_ml_analyse_time_series):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_analyse_time_series),
    )


@pytest.fixture
def mqtt_multiple_time_series(json_ml_analyse_multiple_time_series):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_analyse_multiple_time_series),
    )


@pytest.fixture
def mqtt_text(json_ml_analyse_text):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_analyse_text),
    )


@pytest.fixture
def mqtt_sensor(json_ml_data_example):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_data_example),
    )


@pytest.fixture
def mqtt_fixtures(mqtt_text, mqtt_sensor, mqtt_time_series, mqtt_multiple_time_series):
    return {
        "text": mqtt_text,
        "sensor": mqtt_sensor,
        "time_series": mqtt_time_series,
        "multiple_time_series": mqtt_multiple_time_series,
    }
