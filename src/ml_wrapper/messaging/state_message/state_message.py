"""
This module provides the logic to create Status messages
"""
import json
import logging

from paho.mqtt.client import Client

from .state_enum import ToolState


class StateMessage:
    """
    This class handles the status message logic
    """

    def __init__(self, topic: str, client: Client, logger: logging.Logger):
        self._state: ToolState = None
        self.kwargs = dict()

        # assert isinstance(client, Client), "I can only accept paho Client"
        self.client = client

        assert logger is not None and isinstance(
            logger, logging.Logger
        ), "Logger has to be provided"
        self.logger: logging.Logger = logger

        assert topic is not None and isinstance(topic, str), "Topic has to be set"
        self.topic = topic

    def _get_message(self):
        """ Returns the message of this objects information """
        message = dict(status=self.state.value)
        message = {
            **message,
            **{key: value for key, value in self.kwargs if isinstance(value, str)},
        }
        return json.dumps(message)

    def can_publish(self) -> bool:
        """
        This function indicates, whether the publish function can be safely invoked
        """
        return (
            self._state is not None
            and isinstance(self._state, ToolState)
            and self.client.is_connected()
        )

    def publish(self):
        """
        This message publishes the state to the given topic
        """
        # assert self._state is not None, "state has to be set"
        # assert (
        #     self.client.is_connected()
        # ), "The StateMessage object can only publish, if the client is connected"
        if self.can_publish():
            self.client.publish(self.topic, payload=self._get_message(), qos=0)
            return
        self.logger.warning("I couldn't publish the state message!")

    @property
    def state(self) -> ToolState:
        """ Returns the protected property for state """
        return self._state

    @state.setter
    def state(self, new_value: ToolState):
        """
        Sets the protected property for state
        :@param new_value: State
        """
        assert isinstance(
            new_value, ToolState
        ), "The value to be set has to be of type ToolState, but received {}".format(
            type(new_value)
        )
        pub_state = new_value is not None and self._state != new_value
        self._state = new_value
        if pub_state:
            self.publish()

    @state.deleter
    def state(self):
        """ Deletes the protected property for state """
        self._state = None
