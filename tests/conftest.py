"""
Basic conftest file for root level
"""
import json

import pytest

from ml_wrapper.json_provider import *

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
def ml_mock_fft():
    return FFT


@pytest.fixture
def ml_mock_bad_topic_tool():
    return BadTopicTool


@pytest.fixture
def ml_mock_slow_mltool():
    return SlowMLTool


@pytest.fixture
def ml_mock_result_type_tool():
    return ResultTypeTool


@pytest.fixture
def ml_mock_bad_mltool():
    return BadMLTool


@pytest.fixture
def ml_mock_require_certain_input():
    return RequireCertainInput
