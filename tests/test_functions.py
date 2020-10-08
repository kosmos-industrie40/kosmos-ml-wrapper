"""
This file provides tests for the helper file
"""
import pytest
from ml_wrapper import MessageType
from ml_wrapper.helper import topic_splitter


from unittest import TestCase

from ml_wrapper.json_validator import (
    NonSchemaConformJsonPayload,
    validate_formal,
    validate_trigger,
)

# ----
# Tests for the helper module
# ----


def test_topic_splitter(split_topics):
    with pytest.raises(AssertionError):
        topic_splitter(dict(test=True))
    assert split_topics == topic_splitter(",".join(split_topics))
    assert split_topics == topic_splitter(", ".join(split_topics))
    assert ["a", "b"] == topic_splitter("a,b")
    assert ["a", "b"] == topic_splitter("a|b", sep="|")
    assert ["a/b/c"] == topic_splitter("a/b/c", sep="|")


# ----
# ----
# Tests for the json_validator module
# ----


def test_validate_formal(
    json_data_example_3, json_analyse_time_series, json_ml_analyse_text
):
    assert validate_formal(json_data_example_3) == MessageType.SENSOR_UPDATE
    assert validate_formal(json_analyse_time_series) == MessageType.ANALYSES_Result
    bad_json = json_analyse_time_series
    bad_json["body"]["timestamp"] = 12345
    with pytest.raises(NonSchemaConformJsonPayload):
        validate_formal('{"test": 1}')
    with pytest.raises(NonSchemaConformJsonPayload):
        validate_formal(bad_json)
    del bad_json["body"]["timestamp"]
    with pytest.raises(NonSchemaConformJsonPayload):
        validate_formal(bad_json)


def test_validate_trigger(
    json_ml_analyse_text,
    json_ml_data_example,
    json_analyse_time_series,
    json_data_example_3,
):
    json_ml_analyse_text["body"]["payload"] = json_analyse_time_series
    validate_trigger(json_ml_analyse_text)
    json_ml_data_example["body"]["payload"] = json_data_example_3
    validate_trigger(json_ml_data_example)
    json_ml_analyse_text["body"]["payload"]["body"] = "corrupt"
    with pytest.raises(NonSchemaConformJsonPayload):
        validate_trigger(json_ml_analyse_text)
