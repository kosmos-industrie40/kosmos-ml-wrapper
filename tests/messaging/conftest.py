import json
import logging

import pytest
from ml_wrapper import IncomingMessage
from paho.mqtt.client import MQTTMessage


@pytest.fixture
def new_incoming_message():
    return IncomingMessage(logger=logging.getLogger(__file__))


# pylint: disable=super-init-not-called
class MQTTMessageMock(MQTTMessage):
    """ Mocking Message """

    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload


@pytest.fixture
def mqtt_time_series(json_ml_analyse_time_series):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_analyse_time_series),
    )


@pytest.fixture
def mqtt_multiple_time_series(json_ml_analyse_multiple_time_series):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_analyse_multiple_time_series),
    )


@pytest.fixture
def mqtt_fixtures(mqtt_text, mqtt_sensor, mqtt_time_series, mqtt_multiple_time_series):
    return {
        "text": mqtt_text,
        "sensor": mqtt_sensor,
        "time_series": mqtt_time_series,
        "multiple_time_series": mqtt_multiple_time_series,
    }


@pytest.fixture
def mqtt_text(json_ml_analyse_text):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_analyse_text),
    )


@pytest.fixture
def mqtt_sensor(json_ml_data_example):
    return MQTTMessageMock(
        b"kosmos/analytics/analyse.test-tool/v0.1.-2",
        json.dumps(json_ml_data_example),
    )
