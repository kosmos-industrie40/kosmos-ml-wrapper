""" This module provides a mock for testing of this package """
from paho.mqtt.client import MQTTMessage


class MockMqttClient:
    """ Mock of a mqtt client """

    def __init__(self, logger):
        self.logger = logger
        self.on_message = None
        self.connect = lambda *args, **kwargs: None
        self.subscribe = lambda *args, **kwargs: None

    def mock_a_message(self, client, message: str):
        """ This function can be used to inject a mocked message """
        assert (
            self.on_message is not None
        ), "Please overwrite the clients on_message property with your custom function"
        msg = MQTTMessage
        msg.payload = message
        # pylint: disable=not-callable
        self.on_message(client, None, msg)

    def publish(self, topic, payload):
        """ Provides a publish function """
        self.logger.info("{}:\t{}".format(str(topic), str(payload)))