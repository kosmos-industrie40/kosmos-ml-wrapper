"""
This module tests the conversion of the data
"""
import unittest
from os.path import dirname, join
import pandas as pd
import numpy as np

from src.ml_wrapper.json_provider import (
    JSON_ANALYSE_TIME_SERIES,
    JSON_ANALYSE_MULTIPLE_TIME_SERIES,
    JSON_ANALYSE_TEXT,
    JSON_DATA_EXAMPLE_3,
    JSON_DATA_EXAMPLE,
    JSON_DATA_EXAMPLE_2,
)
from src.ml_wrapper.convert_data import (
    resolve_data_frame,
    retrieve_dataframe,
    retrieve_sensor_update_data,
)

JSON_PATH = join(dirname(__file__), "..", "docs", "MqttPayloads")


def create_df():
    """
    Create a time series with random entries.
    Serves to simulate an external analysis module which publishes results to
    the MQTT broker.
    """
    data1 = np.random.random(5)
    data2 = np.random.random(5)
    data3 = np.random.random(5)
    pdf = pd.DataFrame({"col1": data1, "col2": data2, "col3": data3})
    return pdf


class TestDataRetrievalAndResolve(unittest.TestCase):
    """
    Test Case for data retrieval
    """

    def test_resolve_dataframe(self):
        data = pd.DataFrame(
            {
                "time": [
                    "2020-01-20T10:10:00",
                    "2020-01-20T10:10:02",
                    "2020-01-20T10:10:04",
                    "2020-01-20T10:10:05",
                    "2020-01-20T10:10:06",
                ],
                "value": [1, 2, 3, 4, 5],
                "float_value": [0.0, 0.1, 0.2, 0.3, 0.4],
            },
        ).astype({"time": "datetime64[ns]", "value": int, "float_value": float})
        columns, data = resolve_data_frame(data)
        self.assertEqual(
            columns,
            [
                {"name": "time", "type": "rfctime"},
                {"name": "value", "type": "number"},
                {"name": "float_value", "type": "number"},
            ],
        )
        self.assertTrue(
            np.array_equal(
                data,
                np.array(
                    [
                        ["2020-01-20 10:10:00", "1", "0.0"],
                        ["2020-01-20 10:10:02", "2", "0.1"],
                        ["2020-01-20 10:10:04", "3", "0.2"],
                        ["2020-01-20 10:10:05", "4", "0.3"],
                        ["2020-01-20 10:10:06", "5", "0.4"],
                    ]
                ),
            )
        )

    def test_analysis_time_series(self):
        # test analysis time series
        print("Testing with analyses-example-time_series.json")
        data_frame, columns, data = retrieve_dataframe(
            JSON_ANALYSE_TIME_SERIES.get("results")
        )
        timestamp = JSON_ANALYSE_TIME_SERIES.get("timestamp")
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertIsInstance(timestamp, str)

    def test_analysis_multiple_time_series(self):
        # test analysis time series
        print("Test with analyses-example-multiple_time_series.json")
        timestamp = JSON_ANALYSE_MULTIPLE_TIME_SERIES.get("timestamp")
        self.assertIsInstance(timestamp, str)
        for result in JSON_ANALYSE_MULTIPLE_TIME_SERIES.get("results"):
            data_frame, columns, data = retrieve_dataframe(result)
            self.assertIsInstance(data_frame, pd.DataFrame)
            self.assertIsInstance(columns, list)
            self.assertIsInstance(data, list)

    def test_analysis_text(self):
        # test analysis text
        print("Testing with analyses-example-text.json")
        data = JSON_ANALYSE_TEXT.get("results")
        timestamp = JSON_ANALYSE_TEXT.get("timestamp")
        self.assertIsInstance(data, dict)
        self.assertIsInstance(timestamp, str)

    def test_dataframe_types_retrieval(self):
        print("Testing with data-example-3.json")
        data_frame, _, _, _ = retrieve_sensor_update_data(JSON_DATA_EXAMPLE_3)
        self.assertEqual(
            data_frame.dtypes.tolist(), ["float64", "float64", "datetime64[ns]"]
        )

    def test_sensor_without_metadata(self):
        # test sensor data w/o metadata
        print("Testing with data-example.json")
        data_frame, columns, data, metadata = retrieve_sensor_update_data(
            JSON_DATA_EXAMPLE
        )
        timestamp = JSON_DATA_EXAMPLE.get("timestamp")
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertTrue(metadata is None)
        print(timestamp)
        self.assertIsInstance(timestamp, str)

    def test_sensor_with_metadata(self):
        # test sensor data w/ metadata
        print("Testing with data-example-2.json")
        data_frame, columns, data, metadata = retrieve_sensor_update_data(
            JSON_DATA_EXAMPLE_2
        )
        timestamp = JSON_DATA_EXAMPLE_2.get("timestamp")
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertTrue(metadata is not None)
        self.assertIsInstance(metadata, (dict, list))
        self.assertIsInstance(timestamp, str)


if __name__ == "__main__":
    unittest.main()
