from typing import Union, List

import pandas as pd
import pytest
from examples.usage_example import AnalysisTool
from ml_wrapper import MLWrapper, OutgoingMessage, ResultType
from ml_wrapper.mocks import MockMqttClient
from ml_wrapper.mocks import create_mock_tool


class AsyncTool(MLWrapper):
    async def run(self, out_message: OutgoingMessage) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        self.logger.warning("I am running")
        return {"total": "Yeji", "predict": 100}

    async def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        self.logger.info("here I really resolve")
        return await super().resolve_result_data(result, out_message)


def test_mock_creation(mqtt_time_series):
    MockTool = create_mock_tool(AsyncTool)
    with MockTool(result_type=ResultType.TEXT) as tool:
        tool._react_to_message(None,None, mqtt_time_series)


def test_me(mqtt_time_series):
    with AsyncTool(result_type=ResultType.TEXT) as tool:
        tool._react_to_message(None,None,mqtt_time_series)
