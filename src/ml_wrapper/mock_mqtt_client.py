""" This module provides a mock for testing of this package """
from .helper import generate_mqtt_message_mock


class MockMqttClient:
    """ Mock of a mqtt client """

    def __init__(self, logger):
        self.logger = logger
        self.on_message = None
        self.connect = lambda *args, **kwargs: None
        self.subscriptions = list()
        self.last_published = None

    def subscribe(self, topic, qos):
        """ Cache subscriptions """
        self.subscriptions.append({"topic": topic, "qos": qos})

    def mock_a_message(self, client, message: str):
        """ This function can be used to inject a mocked message """
        assert (
            self.on_message is not None
        ), "Please overwrite the clients on_message property with your custom function"
        msg = generate_mqtt_message_mock(
            "kosmos/analytics/mock_model/mock_tag", message
        )
        # pylint falsly thinks on_message is not callable
        # pylint: disable=not-callable
        self.on_message(client, None, msg)

    def publish(self, topic, payload):
        """ Provides a publish function """
        self.logger.debug("{}:\t{}".format(str(topic), str(payload)))
        self.last_published = payload
