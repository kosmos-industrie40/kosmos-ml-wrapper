"""
Tests threading use cases
"""
import json

from ml_wrapper import MessageType, ResultType


def test_multiple_messages_with_failing_in_between(
    ML_MOCK_REQUIRE_CERTAIN_INPUT,
    json_ml_data_example,
    json_ml_analyse_time_series,
    json_ml_analyse_text,
    caplog,
):
    with ML_MOCK_REQUIRE_CERTAIN_INPUT as tool:
        tool._only_react_to_message_type = MessageType.SENSOR_UPDATE
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_data_example))
        tool._only_react_to_message_type = MessageType.ANALYSES_RESULT
        tool._only_react_to_previous_result_types = [ResultType.TIME_SERIES]
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_time_series))
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_text))
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_analyse_time_series))
    assert any("WrongMessageType" in msg for msg in caplog.messages)
    print(caplog.messages)
