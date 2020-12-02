"""
This clss provides helper functions
"""
import re
from typing import List

import pandas as pd
from paho.mqtt.client import MQTTMessage

from .result_type import ResultType
from .exceptions import InvalidTopic


# pylint: disable=no-else-return
def find_result_type(result) -> ResultType:
    """
    This method checks a few conditions to find the ResultType of a message. If none is matching,
    None is returned.

    @param result: the result to be checked
    @return: ResultType
    """
    checks = [
        isinstance(result, pd.DataFrame),
        isinstance(result, list),
        isinstance(result, dict),
    ]
    if not any(checks) or sum(checks) != 1:
        return None
    if checks[0]:
        return ResultType.TIME_SERIES
    elif checks[1] and all([isinstance(res, pd.DataFrame) for res in result]):
        return ResultType.MULTIPLE_TIME_SERIES
    elif checks[2] and all([key in result.keys() for key in ["total", "predict"]]):
        return ResultType.TEXT
    else:
        return None


def topic_splitter(topic_string: str, sep: str = ",") -> List[str]:
    """
    Splits topic string into topics by separator sep.
    @param sep: str
    @param topic_string: str
    @return: List[str]
    """
    assert isinstance(topic_string, str), "I can only handle strings"
    if topic_string == "":
        return []
    topic_list = topic_string.split(sep)
    for ind, topic in enumerate(topic_list):
        if re.match(r"^/?([^/]+/)*[^/]+/?$", topic) is None:
            raise InvalidTopic("Topic '{}' is not a valid topic.".format(topic))
        topic_list[ind] = topic.strip()
    return topic_list


def generate_mqtt_message_mock(
    topic="kosmos/analytics/mock_model/mock_tag", message=""
):
    """
    Generates an MQTTMessage class object.
    @param topic: str
    @param message: str
    @return: MQTTMessage
    """
    msg = MQTTMessage
    msg.topic = topic
    msg.payload = message
    return msg
