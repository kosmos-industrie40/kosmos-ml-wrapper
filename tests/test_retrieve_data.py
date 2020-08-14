"""
Test the retrieval of data
"""
import unittest
import os

import pandas as pd
from ml_wrapper.convert_data import retrieve_data

JSON_PATH = os.path.join(os.path.dirname(__file__), "../docs/MqttPayloads/")


class TestDataRetrieval(unittest.TestCase):
    """
    Test Case for data retrieval
    """

    def test_analysis_time_series(self):
        # test analysis time series
        with open(JSON_PATH + "analyses-example-time_series.json") as file:
            time_series_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(
            time_series_payload
        )
        self.assertTrue(isinstance(data_frame, pd.DataFrame))
        self.assertTrue(isinstance(columns, list))
        self.assertTrue(isinstance(data, list))
        self.assertTrue(metadata is None)
        self.assertTrue(isinstance(timestamp, int))

    def test_analysis_text(self):
        # test analysis text
        with open(JSON_PATH + "analyses-example-text.json") as file:
            text_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(text_payload)
        self.assertTrue(isinstance(data_frame, pd.DataFrame))
        self.assertTrue(isinstance(columns, list))
        self.assertTrue(isinstance(data, dict))
        self.assertTrue(metadata is None)
        self.assertTrue(isinstance(timestamp, int))

    # def test_analysis_mutliple_time_series(self):
    #     # test analysis time series
    #     with open(JSON_PATH + "analyses-example-multiple_time_series.json") as f:
    #         time_series_payload = f.read()

    #     df, columns, data, metadata, timestamp = retrieve_data(time_series_payload)
    #     self.assertTrue(isinstance(df, list))
    #     self.assertTrue(isinstance(columns, list))
    #     self.assertTrue(isinstance(data, list))
    #     self.assertTrue(metadata is None)
    #     self.assertTrue(isinstance(timestamp, int))

    def test_sensor_without_metadata(self):
        # test sensor data w/o metadata
        with open(JSON_PATH + "data-example.json") as file:
            sensor_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(sensor_payload)
        self.assertTrue(isinstance(data_frame, pd.DataFrame))
        self.assertTrue(isinstance(columns, list))
        self.assertTrue(isinstance(data, list))
        self.assertTrue(metadata is None)
        self.assertTrue(isinstance(timestamp, int))

    def test_sensor_with_metadata(self):
        # test sensor data w/ metadata
        with open(JSON_PATH + "data-example-2.json") as file:
            sensor_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(sensor_payload)
        self.assertTrue(isinstance(data_frame, pd.DataFrame))
        self.assertTrue(isinstance(columns, list))
        self.assertTrue(isinstance(data, list))
        self.assertTrue(metadata is not None)
        self.assertTrue(isinstance(metadata, (dict, list)))
        self.assertTrue(isinstance(timestamp, int))


if __name__ == "__main__":
    unittest.main()
