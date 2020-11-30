"""
This module presents an example of a possible ML Tool Unittest using the ML Wrapper
"""
# This is only required for testing inside the ML Wrapper package
# pylint: disable=redefined-builtin,wrong-import-position
# pylint: disable=duplicate-code,useless-super-delegation,redefined-outer-name

# This is required for you to write in order to create your own ML Tool
import json

import pytest

from ml_wrapper.mocks import create_mock_tool
from ml_wrapper.messaging import JSON_ML_ANALYSE_TIME_SERIES as ml_time_series

from .usage_example import AnalysisTool

AnalysisToolMock = create_mock_tool(AnalysisTool)

# This goes in conftest.py


@pytest.fixture
def patch_env(monkeypatch):
    """
    Patches os settings required for your tool to run
    """
    monkeypatch.setenv("CONFIG_MODEL_URL", "test_url")
    monkeypatch.setenv("CONFIG_MODEL_TAG", "test_tag")
    monkeypatch.setenv("CONFIG_MODEL_FROM", "test_from")


# pylint: disable=unused-argument
@pytest.fixture
def MOCK(patch_env):
    """
    Provides a mock instance of your tool
    """
    return AnalysisTool()


@pytest.fixture
def JSON_ML_ANALYSE_TIME_SERIES():
    """
    Provides the json string of an ML Analyse Time Series Message
    """
    return json.dumps(ml_time_series)


# This goes in your testfile
def test_my_ml_logic(MOCK, JSON_ML_ANALYSE_TIME_SERIES, caplog):
    """
    Tests whether the tool run succesfully
    """
    with MOCK as mock:
        mock.client.mock_a_message(mock.client, JSON_ML_ANALYSE_TIME_SERIES)
    print(caplog.messages)
    assert "Starting all components..." in " ".join(caplog.messages)
    assert all([out is not None for out in mock.out_messages])
