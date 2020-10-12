"""
This module test the {{ cookiecutter.ml_class_name }}.
"""

from time import sleep

import pytest


# Test the run of the tool with normal message
def test_run(MOCK_TOOL, payloads_prerendered):
    with MOCK_TOOL as mock_tool:
        {%- if cookiecutter.only_react_to_message_type == "sensor" %}
        mock_tool.client.mock_a_message(mock_tool.client, payloads_prerendered["JSON_ML_DATA_EXAMPLE"]["json_string"])
        {% else %}
        mock_tool.client.mock_a_message(mock_tool.client, payloads_prerendered["JSON_ML_ANALYSE_TIME_SERIES"]["json_string"])
        {% endif -%}
        mock_tool.logger.info("Done with the work")
        assert all([out is not None for out in mock_tool.out_messages])

# Parameterize your tests
@pytest.mark.parametrize("json_key", [
{%- if cookiecutter.only_react_to_message_type == "sensor" %}
"JSON_ML_DATA_EXAMPLE",
"JSON_ML_DATA_EXAMPLE_3",
"JSON_ML_DATA_EXAMPLE_2",
{% elif cookiecutter.only_react_to_message_type == "analyses" %}
"JSON_ML_ANALYSE_TEXT",
"JSON_ML_ANALYSE_TIME_SERIES",
"JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES",
{% else %}
"JSON_ML_ANALYSE_TEXT",
"JSON_ML_ANALYSE_TIME_SERIES",
"JSON_ML_ANALYSE_MULTIPLE_TIME_SERIES",
"JSON_ML_DATA_EXAMPLE",
"JSON_ML_DATA_EXAMPLE_3",
"JSON_ML_DATA_EXAMPLE_2",
{% endif -%}
])
def test_multiple_runs(MOCK_TOOL, payloads_prerendered, json_key):
    with MOCK_TOOL as mock_tool:
        mock_tool.client.mock_a_message(
            mock_tool.client,
            payloads_prerendered[json_key]["json_string"]
        )
        mock_tool.logger.info("Done with the work")
        assert all([out is not None for out in mock_tool.out_messages])
