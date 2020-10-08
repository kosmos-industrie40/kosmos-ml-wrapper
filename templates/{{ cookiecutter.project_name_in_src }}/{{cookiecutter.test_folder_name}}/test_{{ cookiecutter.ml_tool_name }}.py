"""
This module test the {{ cookiecutter.ml_class_name }}.
"""

from time import sleep

import pytest


# Test the run of the tool with normal message
def test_run(mock_tool, payloads_prerendered):
    {%- if cookiecutter.only_react_to_message_type == "sensor" %}
    mock_tool.client.mock_a_message(mock_tool.client, payloads_prerendered["JSON_ML_DATA_EXAMPLE"]["json_string"])
    {% else %}
    mock_tool.client.mock_a_message(mock_tool.client, payloads_prerendered["JSON_ML_ANALYSE_TIME_SERIES"]["json_string"])
    {% endif -%}
    while mock_tool.async_not_ready():
        sleep(1)
    mock_tool.logger.info("Done with the Thread work")
    assert mock_tool.last_result is not None

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
def test_multiple_runs(mock_tool, payloads_prerendered, json_key):
    mock_tool.client.mock_a_message(
        mock_tool.client,
        payloads_prerendered[json_key]["json_string"]
    )
    while mock_tool.async_not_ready():
        sleep(1)
    mock_tool.logger.info("Done with the Thread work")
    assert mock_tool.last_result is not None
