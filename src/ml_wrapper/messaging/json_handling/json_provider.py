"""
This file provides the json schemas and json examples from the docs.
"""

from os.path import dirname, abspath, join
import json

FILE_DIR = dirname(abspath(__file__))
SCHEMA_DIR = abspath(join(FILE_DIR, "kosmos_json_specifications", "mqtt_payloads"))
SUB_SCHEMA = lambda x="ml-trigger": join(SCHEMA_DIR, x)
SUB_SCHEMA_FILE = lambda path, file: join(SUB_SCHEMA(path), file)

FORMAL_REPLACES = {
    ref: "{}".format("file://{}".format(join(SUB_SCHEMA(key), "formal.json")))
    for key, ref in {
        "analysis": "file:analysis/formal.json",
        "data": "file:data/formal.json",
        "ml-trigger": "file:ml-trigger/formal.json",
    }.items()
}


def _create_replaces(path):
    dict_ = {
        "file:formal.json": "file://{}".format(
            SUB_SCHEMA_FILE(path=path, file="formal.json")
        ),
        "file:data/formal.json": "file://{}".format(
            SUB_SCHEMA_FILE(path="data", file="formal.json")
        ),
        "file:analysis/formal.json": "file://{}".format(
            SUB_SCHEMA_FILE(path="analysis", file="formal.json")
        ),
    }
    return dict_


def _replace_file_refs(content_, path):
    repl_ = _create_replaces(path)
    # print(repl_)
    for key, item in repl_.items():
        content_ = content_.replace(key, item)
    return content_


def _read_json(file_, path="ml-trigger"):
    result = None
    with open(join(SUB_SCHEMA(path), file_)) as file:
        # result = json.loads(file.read())
        result = json.loads(_replace_file_refs(file.read(), path=path))
    return result


def _combine_ml_and_example(file_, path="ml-trigger", analyse=True):
    result = _read_json(
        "analysis-example.json" if analyse else "update-example.json", path="ml-trigger"
    )
    with open(join(SUB_SCHEMA(path), file_)) as file:
        result["body"]["payload"] = json.loads(
            _replace_file_refs(file.read(), path=path)
        )
    return result


ANALYSES_FORMAL = _read_json("formal.json", path="analysis")
DATA_FORMAL = _read_json("formal.json", path="data")
TRIGGER_FORMAL = _read_json("formal.json", path="ml-trigger")

ANALYSES_FORMAL["$id"] = ""
DATA_FORMAL["$id"] = ""
TRIGGER_FORMAL["$id"] = ""

SCHEMA_STORE = {
    ANALYSES_FORMAL["$id"]: ANALYSES_FORMAL,
    DATA_FORMAL["$id"]: DATA_FORMAL,
    TRIGGER_FORMAL["$id"]: TRIGGER_FORMAL,
}

JSON_ML_ANALYSE_TIME_SERIES = _combine_ml_and_example(
    "example-time_series.json", path="analysis"
)
JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES = _combine_ml_and_example(
    "example-multiple_time_series.json", path="analysis"
)
JSON_ML_ANALYSE_TEXT = _combine_ml_and_example("example-text.json", path="analysis")
JSON_ML_DATA_EXAMPLE = _combine_ml_and_example(
    "example.json", path="data", analyse=False
)
JSON_ML_DATA_EXAMPLE_2 = _combine_ml_and_example(
    "example-2.json", path="data", analyse=False
)
JSON_ML_DATA_EXAMPLE_3 = _combine_ml_and_example(
    "example-3.json", path="data", analyse=False
)
JSON_ML_DATA_EXAMPLE_AXISTEST = _combine_ml_and_example(
    "example-axistest.json", path="data", analyse=False
)

JSON_ANALYSE_TIME_SERIES = _read_json("example-time_series.json", path="analysis")
JSON_ANALYSE_MULTIPLE_TIME_SERIES = _read_json(
    "example-multiple_time_series.json", path="analysis"
)
JSON_ANALYSE_TEXT = _read_json("example-text.json", path="analysis")
JSON_DATA_EXAMPLE = _read_json("example.json", path="data")
JSON_DATA_EXAMPLE_2 = _read_json("example-2.json", path="data")
JSON_DATA_EXAMPLE_3 = _read_json("example-3.json", path="data")
JSON_DATA_EXAMPLE_AXISTEST = _read_json("example-axistest.json", path="data")
