"""
This file provides a testing mock for your ML Tool
"""
from typing import List, Union

import pandas as pd

from ml_wrapper import OutgoingMessage
from {{ cookiecutter.project_name_in_src }} import {{ cookiecutter.ml_class_name }}
from ml_wrapper.mock_mqtt_client import MockMqttClient

class {{ cookiecutter.ml_class_name }}Mock({{ cookiecutter.ml_class_name }}):
    """
    This mock is used to test your application in a running context
    """

    def __init__(self):
        """Initialize Mock"""
        super().__init__()
        self.last_result = None

    # pylint: disable=attribute-defined-outside-init
    def _init_mqtt(self):
        """
        Proivde a mock client of the mqtt client
        """
        self.client = MockMqttClient(self.logger)

    def resolve_result_data(
            self,
            result: Union[pd.DataFrame, List[pd.DataFrame], dict],
            out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        """
        Saves the resolved data
        """
        self.last_result = result
        return super().resolve_result_data(result, out_message)
