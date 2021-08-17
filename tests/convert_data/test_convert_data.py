"""
This module tests the conversion of the data
"""
from os.path import dirname, join

import numpy as np
import pandas as pd

from ml_wrapper.messaging.json_handling import (
    resolve_data_frame,
    retrieve_dataframe,
    retrieve_sensor_update_data,
)

JSON_PATH = join(dirname(__file__), "..", "docs", "MqttPayloads")


def test_resolve_dataframe(data):
    columns, data = resolve_data_frame(data)
    assert columns == [
        {"name": "time", "type": "rfctime"},
        {"name": "value", "type": "number"},
        {"name": "float_value", "type": "number"},
    ]
    assert np.array_equal(
        data,
        np.array(
            [
                [
                    "2020-01-20 10:10:00",
                    "2020-01-20 10:10:02",
                    "2020-01-20 10:10:04",
                    "2020-01-20 10:10:05",
                    "2020-01-20 10:10:06",
                ],
                ["1", "2", "3", "4", "5"],
                ["0.0", "0.1", "0.2", "0.3", "0.4"],
            ]
        ),
    )


def test_analysis_time_series(json_analyse_time_series):
    # test analysis time series
    print("Testing with analyses-example-time_series.json")
    data_frame, columns, data = retrieve_dataframe(
        json_analyse_time_series["body"].get("results")
    )
    timestamp = json_analyse_time_series["body"].get("timestamp")
    assert isinstance(data_frame, pd.DataFrame)
    assert isinstance(columns, list)
    assert isinstance(data, list)
    assert isinstance(timestamp, str)


def test_analysis_multiple_time_series(json_analyse_multiple_time_series):
    # test analysis time series
    print("Test with analyses-example-multiple_time_series.json")
    timestamp = json_analyse_multiple_time_series["body"].get("timestamp")
    assert isinstance(timestamp, str)
    for result in json_analyse_multiple_time_series["body"].get("results"):
        data_frame, columns, data = retrieve_dataframe(result)
        assert isinstance(data_frame, pd.DataFrame)
        assert isinstance(columns, list)
        assert isinstance(data, list)


def test_analysis_text(json_analyse_text):
    # test analysis text
    print("Testing with analyses-example-text.json")
    data = json_analyse_text["body"].get("results")
    timestamp = json_analyse_text["body"].get("timestamp")
    assert isinstance(data, dict)
    assert isinstance(timestamp, str)


def test_dataframe_types_retrieval(json_data_example_3):
    print("Testing with data-example-3.json")
    data_frame, _, _, _, _ = retrieve_sensor_update_data(json_data_example_3["body"])
    assert data_frame.dtypes.tolist() == ["float64", "float64", "datetime64[ns]"]


def test_sensor_without_metadata(json_data_example):
    # test sensor data w/o metadata
    print("Testing with data-example.json")
    data_frame, columns, data, metadata, column_meta = retrieve_sensor_update_data(
        json_data_example["body"]
    )
    timestamp = json_data_example["body"].get("timestamp")
    assert isinstance(data_frame, pd.DataFrame)
    assert isinstance(columns, list)
    assert isinstance(data, list)
    assert metadata is None
    print(timestamp)
    assert isinstance(timestamp, str)
    assert isinstance(column_meta, dict)
    assert "unit" in column_meta[columns[0]["name"]]
    assert "description" in column_meta[columns[0]["name"]]
    assert "future" in column_meta[columns[0]["name"]]


def test_sensor_with_metadata(json_data_example_2):
    # test sensor data w/ metadata
    print("Testing with data-example-2.json")
    data_frame, columns, data, metadata, column_meta = retrieve_sensor_update_data(
        json_data_example_2["body"]
    )
    timestamp = json_data_example_2["body"].get("timestamp")
    assert isinstance(data_frame, pd.DataFrame)
    assert isinstance(columns, list)
    assert isinstance(data, list)
    assert metadata is not None
    assert isinstance(metadata, (dict, list))
    assert isinstance(timestamp, str)
    assert isinstance(column_meta, dict)
    assert "unit" in column_meta[columns[0]["name"]]
    assert "description" in column_meta[columns[0]["name"]]
    assert "future" in column_meta[columns[0]["name"]]
