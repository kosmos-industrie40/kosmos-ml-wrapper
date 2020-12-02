"""
Conftest is like the setup for your pytests.
This provides pytest fixtures for all tests
"""
# pylint: disable=redefined-builtin,wrong-import-position,duplicate-code,unused-argument
# pylint: disable=protected-access
import json

import pytest

from ml_wrapper.mocks import create_mock_tool
from ml_wrapper.messaging import (
    JSON_ML_ANALYSE_TEXT,
    JSON_ML_DATA_EXAMPLE,
    JSON_ML_ANALYSE_TIME_SERIES,
    JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES,
    JSON_ML_DATA_EXAMPLE_3,
    JSON_ML_DATA_EXAMPLE_2
)

from {{ cookiecutter.project_name_in_src }} import {{ cookiecutter.ml_class_name }}

MockTool = create_mock_tool({{ cookiecutter.ml_class_name }})

@pytest.fixture
def patch_env(monkeypatch):
    """
    Patches os settings required for your tool to run
    """
    monkeypatch.setenv("CONFIG_MODEL_URL","test_url")
    monkeypatch.setenv("CONFIG_MODEL_TAG","test_tag")
    monkeypatch.setenv("CONFIG_MODEL_FROM","test_from")

@pytest.fixture
def MOCK_TOOL(patch_env):
    """
    Provides a mocked instance of your ML Tool
    """
    return MockTool()

@pytest.fixture
def possible_example_json_payloads():
    """
    Provides the payloads available
    """
    payloads = {
        "JSON_ML_ANALYSE_TEXT": JSON_ML_ANALYSE_TEXT,
        "JSON_ML_DATA_EXAMPLE": JSON_ML_DATA_EXAMPLE,
        "JSON_ML_ANALYSE_TIME_SERIES": JSON_ML_ANALYSE_TIME_SERIES,
        "JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES": JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES,
        "JSON_ML_DATA_EXAMPLE_3": JSON_ML_DATA_EXAMPLE_3,
        "JSON_ML_DATA_EXAMPLE_2": JSON_ML_DATA_EXAMPLE_2
    }
    return payloads

@pytest.fixture
def payloads_prerendered(possible_example_json_payloads):
    """
    Provide the payload string and dictionary available
    """
    dict_ = dict()
    for name in possible_example_json_payloads.keys():
        json_ = possible_example_json_payloads[name]
        dict_[name] = dict(
            json=json_,
            json_string=json.dumps(json_)
        )
    return dict_
