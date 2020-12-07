"""
This module tests the state report functionality
"""

import json
from unittest.mock import Mock


def get_status_messages(caplog):
    return [message for message in caplog.messages if "kosmos/status" in message]


def test_state_report_normal(
    ML_MOCK_SIMPLE,
    json_ml_data_example,
    caplog,
):
    with ML_MOCK_SIMPLE as tool:
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_data_example))
        caps = get_status_messages(caplog)
        assert "starting" in " ".join(caps) and "alive" in " ".join(caps)
        assert len(caps) == 2
    del tool.state.state
    assert tool.state.state is None


def test_state_report_fails(
    ML_MOCK_SIMPLE,
    json_ml_data_example,
    caplog,
):
    with ML_MOCK_SIMPLE as tool:
        tool.state.client.is_connected = Mock(return_value=False)
        tool.client.mock_a_message(tool.client, json.dumps(json_ml_data_example))
    assert "I couldn't publish the state message!" in " ".join(caplog.messages)
