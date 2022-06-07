"""
Conftest to provide messaging fixtures
"""
import pytest
import pandas
from ml_wrapper import ResultType, OutgoingMessage


@pytest.fixture
def expect_retrieve_fixture():
    return {
        "text": {
            "result_type": ResultType.TEXT,
            "type": dict,
        },
        "sensor": {
            "result_type": None,
            "type": pandas.DataFrame,
        },
        "sensor_axistest": {
            "result_type": None,
            "type": pandas.DataFrame,
        },
        "time_series": {
            "result_type": ResultType.TIME_SERIES,
            "type": pandas.DataFrame,
        },
        "multiple_time_series": {
            "result_type": ResultType.MULTIPLE_TIME_SERIES,
            "type": list,
        },
    }


@pytest.fixture
def new_outgoing_message_by_incoming_message():
    return lambda incoming_message: OutgoingMessage(
        in_message=incoming_message,
        from_="none",
        model_url="none",
        model_tag="none",
        is_temporary=True,
        temporary_keyword="temporary",
    )
