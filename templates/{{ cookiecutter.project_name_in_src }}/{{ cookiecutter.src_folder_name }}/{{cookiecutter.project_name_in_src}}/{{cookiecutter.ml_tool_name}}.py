"""
This module provides the implementation of the ML Wrapper for the tool
{{ cookiecutter.ml_tool_name }}.
"""
from typing import Union, List
import asyncio
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
        """
        Initialises the {{ cookiecutter.ml_class_name }} Class
        """
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
            only_react_to_message_type = MessageType.ANALYSES_RESULT,
            {%- endif %}
            outgoing_message_is_temporary = True,
            # The outgoing_message_is_temporary needs to be changed,
            # if your results need to be stored!
        )

    async def run(
            self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        # FIXME: Provide a docstring
        self.logger.debug("Starting run method in subthread")
        retrieved_data = out_message.in_message.retrieved_data
        print(retrieved_data)
        {%- if cookiecutter.result_type_of_the_tool == "time_series" %}
        return pd.DataFrame({"message":["I present to you", "the result"]})
        {%- elif cookiecutter.result_type_of_the_tool == "multiple_time_series" %}
        return [pd.DataFrame({"message": ["I present to you", "the results"]}), pd.DataFrame({"result": [100, 200, 2]})]
        {%- elif cookiecutter.result_type_of_the_tool == "text" %}
        return {"total": "This will run", "predict": 97}
        {%- endif %}

    {% if cookiecutter.do_you_want_to_retrieve_data == "yes" %}
    async def retrieve_payload_data(self, in_message: IncomingMessage) -> IncomingMessage:
        # FIXME: Provide a docstring
        self.logger.debug("I need to retrieve additional data")
        # This is the data I retrieved somehow:
        data = pd.DataFrame({"ind": [list(range(10))]})
        # Now I store this information for my run method:
        in_message.custom_information_field = data
        return in_message
    {% endif %}

if __name__ == "__main__":
    with {{ cookiecutter.ml_class_name }}() as {{ cookiecutter.ml_class_name|lower }}:
        {{cookiecutter.ml_class_name | lower}}.logger.info("Startup the ml tool")
        {{cookiecutter.ml_class_name | lower}}.start()
