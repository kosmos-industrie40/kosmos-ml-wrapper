"""
Conftest is like the setup for your pytests.
This provides pytest fixtures for all tests
"""

# pylint: disable=redefined-builtin,wrong-import-position,duplicate-code
import os

os.environ["CONFIG_MODEL_URL"] = "test_url"
os.environ["CONFIG_MODEL_TAG"] = "test_tag"
os.environ["CONFIG_MODEL_FROM"] = "test_from"

import pytest
import json

from ml_wrapper.mocks import create_mock_tool

from ml_wrapper.json_provider import (
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
def MOCK_TOOL():
    return MockTool()

@pytest.fixture
def possible_example_json_payloads():
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
    dict_ = dict()
    for name in possible_example_json_payloads.keys():
        json_ = possible_example_json_payloads[name]
        dict_[name] = dict(
            json=json_,
            json_string=json.dumps(json_)
        )
    return dict_
