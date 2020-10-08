import json
from time import sleep

import pytest
from ml_wrapper import MessageType, ResultType


def test_multiple_messages_with_failing_in_between(
    ml_mock_require_certain_input,
    json_ml_data_example,
    json_ml_analyse_time_series,
    json_ml_analyse_text,
    caplog,
):
    tool = ml_mock_require_certain_input
    tool._only_react_to_message_type = MessageType.SENSOR_UPDATE
    tool.client.mock_a_message(tool.client, json.dumps(json_ml_data_example))
    tool._only_react_to_message_type = MessageType.ANALYSES_Result
    tool._only_react_to_previous_result_types = [ResultType.TIME_SERIES]
    tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_time_series))
    tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_text))
    tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_time_series))
    while tool.async_not_ready():
        sleep(1)
    assert any(["WrongMessageType" in msg for msg in caplog.messages])
    print(caplog.messages)
