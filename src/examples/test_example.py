"""
This module presents an example of a possible ML Tool Unittest using the ML Wrapper
"""
# This is only required for testing inside the ML Wrapper package
# pylint: disable=redefined-builtin,wrong-import-position
# pylint: disable=duplicate-code,useless-super-delegation

# This is required for you to write in order to create your own ML Tool
import json

import pytest

from .usage_example import AnalysisTool
from ml_wrapper.mocks import create_mock_tool
from ml_wrapper.json_provider import JSON_ML_ANALYSE_TIME_SERIES as ml_time_series

AnalysisToolMock = create_mock_tool(AnalysisTool)

# This goes in conftest.py
@pytest.fixture
def MOCK():
    return AnalysisTool()

@pytest.fixture
def JSON_ML_ANALYSE_TIME_SERIES():
    return json.dumps(ml_time_series)

# This goes in your testfile
def test_my_ml_logic(MOCK, JSON_ML_ANALYSE_TIME_SERIES, caplog):
    with MOCK as mock:
        mock.client.mock_a_message(mock.client, JSON_ML_ANALYSE_TIME_SERIES)
    print(caplog.messages)
    assert "Starting all components..." in " ".join(caplog.messages)
