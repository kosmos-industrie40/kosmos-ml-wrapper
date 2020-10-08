import pytest

import pandas as pd


@pytest.fixture
def data():
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
    return data

@pytest.fixture
def random_df():
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
