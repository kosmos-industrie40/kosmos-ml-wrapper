"""
This module provides the implementation of the ML Wrapper for the tool
{{ cookiecutter.ml_tool_name }}.
"""
from typing import Union, List
import pandas as pd

from ml_wrapper import (
    MLWrapper,
    {% if cookiecutter.do_you_want_to_retrieve_data == "yes" -%}
    IncomingMessage,
    {% endif -%}
    OutgoingMessage,
    ResultType,
    {% if cookiecutter.only_react_to_message_type == "sensor" -%}
    MessageType
    {% elif cookiecutter.only_react_to_message_type == "analyse" -%}
    MessageType
    {% endif %}
)

class {{ cookiecutter.ml_class_name }}(MLWrapper):
    """
    This class provides the functionality XYZ.
    It implements the ML Wrapper class/interface.
    """

    def __init__(self):
        "Initialises the {{ cookiecutter.ml_class_name }} Class"
        super().__init__(result_type=
            {%- if cookiecutter.result_type_of_the_tool == "time_series" -%}
            ResultType.TIME_SERIES
            {%- elif cookiecutter.result_type_of_the_tool == "multiple_time_series" -%}
            ResultType.MULTIPLE_TIME_SERIES
            {%- elif cookiecutter.result_type_of_the_tool == "text" -%}
            ResultType.TEXT
            {%- endif -%},
            {%- if cookiecutter.only_react_to_message_type == "sensor" -%}
            only_react_to_message_type = MessageType.SENSOR_UPDATE,
            {%- elif cookiecutter.only_react_to_message_type == "analyse" -%}
            only_react_to_message_type = MessageType.ANALYSES_Result,
            {%- endif -%}
        )

    def run(
            self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        self.logger.debug("Starting run method in subthread")
        retrieved_data = out_message.in_message.retrieved_data
        {%- if cookiecutter.result_type_of_the_tool == "time_series" %}
        return retrieved_data
        {%- elif cookiecutter.result_type_of_the_tool == "multiple_time_series" %}
        return [retrieved_data]
        {%- elif cookiecutter.result_type_of_the_tool == "text" %}
        return {"total": "This will run", "predict": 97}
        {%- endif %}

    {% if cookiecutter.do_you_want_to_retrieve_data == "yes" %}
    def retrieve_payload_data(self, in_message: IncomingMessage) -> IncomingMessage:
        self.logger.debug("I need to retrieve additional data")
        # This is the data I retrieved somehow:
        data = pd.DataFrame({"ind": [list(range(10))]})
        # Now I store this information for my run method:
        in_message.custom_information_field = data
        return in_message
    {% endif %}

if __name__ == "__main__":
    {{ cookiecutter.ml_class_name|upper }} = {{ cookiecutter.ml_class_name }}()
    {{cookiecutter.ml_class_name | upper}}.logger.info("Startup the ml tool")
    {{cookiecutter.ml_class_name | upper}}.start()
