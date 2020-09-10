"""
This file provides the json schemas and json examples from the docs.
"""

from os.path import dirname, abspath, join
import json

FILE_DIR = dirname(abspath(__file__))
SCHEMA_DIR = abspath(
    join(FILE_DIR, "kosmos-json-specifications", "mqtt_payloads")
)

FORMAL_REPLACES = {
    ref: "{}".format("file://{}".format(join(SCHEMA_DIR, ref)))
    for ref in ["analysis-formal.json", "data-formal.json", "ml-formal.json"]
}


def _replace_file_refs(content_):
    for key in FORMAL_REPLACES:
        content_ = content_.replace(key, FORMAL_REPLACES[key])
    return content_


def _read_json(file_):
    result = None
    with open(join(SCHEMA_DIR, file_)) as file:
        result = json.loads(_replace_file_refs(file.read()))
    return result


def _combine_ml_and_example(file_, analyse=True):
    result = _read_json(
        "ml-analysis-example.json" if analyse else "ml-update-example.json"
    )
    with open(join(SCHEMA_DIR, file_)) as file:
        result["payload"] = json.loads(file.read())
    return result


ANALYSES_FORMAL = _read_json("analysis-formal.json")
DATA_FORMAL = _read_json("data-formal.json")
TRIGGER_FORMAL = _read_json("ml-formal.json")

ANALYSES_FORMAL["$id"] = ""
DATA_FORMAL["$id"] = ""
TRIGGER_FORMAL["$id"] = ""

SCHEMA_STORE = {
    ANALYSES_FORMAL["$id"]: ANALYSES_FORMAL,
    DATA_FORMAL["$id"]: DATA_FORMAL,
    TRIGGER_FORMAL["$id"]: TRIGGER_FORMAL,
}

JSON_ML_ANALYSE_TIME_SERIES = _combine_ml_and_example(
    "analysis-example-time_series.json"
)
JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES = _combine_ml_and_example(
    "analysis-example-multiple_time_series.json"
)
JSON_ML_ANALYSE_TEXT = _combine_ml_and_example("analysis-example-text.json")
JSON_ML_DATA_EXAMPLE = _combine_ml_and_example("data-example.json", analyse=False)
JSON_ML_DATA_EXAMPLE_2 = _combine_ml_and_example("data-example-2.json", analyse=False)
JSON_ML_DATA_EXAMPLE_3 = _combine_ml_and_example("data-example-3.json", analyse=False)

JSON_ANALYSE_TIME_SERIES = _read_json("analysis-example-time_series.json")
JSON_ANALYSE_MULTIPLE_TIME_SERIES = _read_json(
    "analysis-example-multiple_time_series.json"
)
JSON_ANALYSE_TEXT = _read_json("analysis-example-text.json")
JSON_DATA_EXAMPLE = _read_json("data-example.json")
JSON_DATA_EXAMPLE_2 = _read_json("data-example-2.json")
JSON_DATA_EXAMPLE_3 = _read_json("data-example-3.json")
