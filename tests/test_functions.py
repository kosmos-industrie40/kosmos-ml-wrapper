"""
This file provides tests for the helper file
"""
import pandas
import pytest
from ml_wrapper import MessageType, ResultType, InvalidTopic
from ml_wrapper.misc import topic_splitter, find_result_type

from ml_wrapper.messaging import (
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
    with pytest.raises(InvalidTopic):
        topic_splitter("invalid///")
    with pytest.raises(InvalidTopic):
        topic_splitter("invalid//")
    with pytest.raises(InvalidTopic):
        topic_splitter("invalid/on//top/")


@pytest.mark.parametrize(
    "result_input,expected",
    [
        [pandas.DataFrame([1, 2, 3]), ResultType.TIME_SERIES],
        [
            [pandas.DataFrame([1, 2, 3]), pandas.DataFrame([1, 2, 3])],
            ResultType.MULTIPLE_TIME_SERIES,
        ],
        [{"total": "nothing", "predict": 100}, ResultType.TEXT],
        [{}, None],
        ["", None],
    ],
)
def test_find_result_type(result_input, expected):
    assert find_result_type(result=result_input) == expected


# ----
# ----
# Tests for the json_validator module
# ----


def test_validate_formal(json_data_example_3, json_analyse_time_series):
    assert validate_formal(json_data_example_3) == MessageType.SENSOR_UPDATE
    assert validate_formal(json_analyse_time_series) == MessageType.ANALYSES_RESULT
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
