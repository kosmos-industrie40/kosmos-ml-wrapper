"""
This module tests the resolving of the data
"""
import unittest
import json
import time
import os
import pandas as pd
import numpy as np
import jsonschema

from ml_wrapper.convert_data import resolve_data


JSON_PATH = os.path.join(os.path.dirname(__file__), "../docs/MqttPayloads/")


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
        payload = {
            "from": "something",
            "date": int(time.time()),
            "calculated": {"message": 1234, "received": int(time.time())},
        }
        return payload

    def test_send_time_series(self):
        data_frame = create_df()

        payload = resolve_data(data_frame, "time_series")

        with open(JSON_PATH + "analyses-formal.json") as file:
            schema = json.load(file)

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)

    def test_send_multiple_time_series(self):
        df_list = []
        for _ in range(4):
            data_frame = create_df()
            df_list.append(data_frame)

        payload = resolve_data(df_list, "multiple_time_series")

        with open(JSON_PATH + "analyses-formal.json") as file:
            schema = json.load(file)

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)

    def test_send_text(self):
        with open(JSON_PATH + "analyses-formal.json") as file:
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

        with open(JSON_PATH + "analyses-formal.json") as file:
            schema = json.load(file)

        payload.update(self.provide_admin_data())
        jsonschema.validate(payload, schema)


if __name__ == "__main__":
    unittest.main()
