"""
This module tests the conversion of the data
"""
import unittest
import json
import datetime
from os.path import dirname, join
import pandas as pd
import numpy as np
import jsonschema

from ml_wrapper.convert_data import resolve_data, resolve_data_frame, retrieve_data

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


class TestDataResolve(unittest.TestCase):
    """ Testcase for the Retrieval of data """

    def provide_admin_data(self):
        # NB: Need to handle signing and so on in ml wrapper class
        # Use sample data as a stand-in for testing
        now_iso = datetime.datetime.utcnow().isoformat(sep="T")
        payload = {
            "from": "something",
            "timestamp": now_iso,
            "calculated": {
                "message": {"machine": "huckleberry", "sensor": "finn"},
                "received": now_iso,
            },
            "model": {"url": "to/the/infinity", "tag": "and/beyond"},
        }
        return payload

    def test_send_time_series(self):
        data_frame = create_df()

        payload = resolve_data(data_frame, "time_series")

        with open(join(JSON_PATH, "analyses-formal.json")) as file:
            schema = json.load(file)

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)

    def test_send_multiple_time_series(self):
        df_list = []
        for _ in range(4):
            data_frame = create_df()
            df_list.append(data_frame)

        payload = resolve_data(df_list, "multiple_time_series")

        with open(join(JSON_PATH, "analyses-formal.json")) as file:
            schema = json.load(file)

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)

    def test_send_text(self):
        with open(join(JSON_PATH, "analyses-formal.json")) as file:
            schema = json.load(file)

        data1 = {"foo": "bar"}
        self.assertRaises(Exception, resolve_data, data1, "text")

        data2 = {"total": "something"}
        self.assertRaises(Exception, resolve_data, data2, "text")

        data = {"total": "foo", "predict": 987, "anything": {"More": "Data"}}
        payload = resolve_data(data, "text")

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)

    def test_send_something(self):
        data1 = {"foo": "bar"}
        self.assertRaises(Exception, resolve_data, data1, "something")

    def test_send_string(self):
        data_frame = create_df()
        data_frame = data_frame.astype(str)

        payload = resolve_data(data_frame, "time_series")

        with open(join(JSON_PATH, "analyses-formal.json")) as file:
            schema = json.load(file)

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)

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


class TestDataRetrieval(unittest.TestCase):
    """
    Test Case for data retrieval
    """

    def test_analysis_time_series(self):
        # test analysis time series
        with open(join(JSON_PATH, "analyses-example-time_series.json")) as file:
            time_series_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(
            time_series_payload
        )
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertTrue(metadata is None)
        self.assertIsInstance(timestamp, str)

    def test_analysis_text(self):
        # test analysis text
        with open(join(JSON_PATH, "analyses-example-text.json")) as file:
            text_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(text_payload)
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, dict)
        self.assertTrue(metadata is None)
        self.assertIsInstance(timestamp, str)

    # def test_analysis_mutliple_time_series(self):
    #     # test analysis time series
    #     with open(join(JSON_PATH, "analyses-example-multiple_time_series.json")) as f:
    #         time_series_payload = f.read()

    #     df, columns, data, metadata, timestamp = retrieve_data(time_series_payload)
    #     self.assertIsInstance(df, list)
    #     self.assertIsInstance(columns, list)
    #     self.assertIsInstance(data, list)
    #     self.assertTrue(metadata is None)
    #     self.assertIsInstance(timestamp, str)

    def test_retrieval_of_dataframe(self):
        with open(join(JSON_PATH, "data-example-3.json")) as file:
            sensor_payload = file.read()
        print(sensor_payload)
        data_frame, _, _, _, _ = retrieve_data(sensor_payload)
        self.assertEqual(
            data_frame.dtypes.tolist(), ["float64", "float64", "datetime64[ns]"]
        )

    def test_sensor_without_metadata(self):
        # test sensor data w/o metadata
        with open(join(JSON_PATH, "data-example.json")) as file:
            sensor_payload = file.read()

        print(sensor_payload)
        data_frame, columns, data, metadata, timestamp = retrieve_data(sensor_payload)
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertTrue(metadata is None)
        print(timestamp)
        self.assertIsInstance(timestamp, str)

    def test_sensor_with_metadata(self):
        # test sensor data w/ metadata
        with open(join(JSON_PATH, "data-example-2.json")) as file:
            sensor_payload = file.read()

        data_frame, columns, data, metadata, timestamp = retrieve_data(sensor_payload)
        self.assertIsInstance(data_frame, pd.DataFrame)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertTrue(metadata is not None)
        self.assertIsInstance(metadata, (dict, list))
        self.assertIsInstance(timestamp, str)


if __name__ == "__main__":
    unittest.main()
