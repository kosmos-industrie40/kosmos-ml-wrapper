"""
Basic conftest file for root level.
Providing jsons, (mqtt) messages and ml tools as fixtures
"""
import json
import logging

import pytest
from paho.mqtt.client import MQTTMessage

from ml_wrapper import IncomingMessage
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
)


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
def ml_mock_fft():
    return FFT()


@pytest.fixture
def ml_mock_bad_topic_tool():
    return BadTopicTool()


@pytest.fixture
def ml_mock_slow_mltool():
    return SlowMLTool()


@pytest.fixture
def ml_mock_result_type_tool():
    return ResultTypeTool()


@pytest.fixture
def ml_mock_bad_mltool():
    return BadMLTool()


@pytest.fixture
def ml_mock_require_certain_input():
    return RequireCertainInput()


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
