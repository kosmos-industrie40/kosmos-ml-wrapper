""" This module provides a mock for testing of this package """
import json
import logging
from typing import Type, List, Union
import pandas as pd
import inspect
from ml_wrapper import MLWrapper
from .messaging import OutgoingMessage

from .helper import generate_mqtt_message_mock


class MockMqttClient:
    """ Mock of a mqtt client """

    def __init__(self, logger):
        self.logger = logger
        self.on_message = None
        self.connect = lambda *args, **kwargs: None
        self.subscriptions = list()
        self.last_published = None
        self.loop_forever = lambda: None
        self.loop_stop = lambda: None
        self.disconnect = lambda: None

    def subscribe(self, topic, qos):
        """ Cache subscriptions """
        self.subscriptions.append({"topic": topic, "qos": qos})

    def mock_a_message(self, client, message: str):
        """ This function can be used to inject a mocked message """
        assert (
            self.on_message is not None
        ), "Please overwrite the clients on_message property with your custom function"
        if isinstance(message, dict):
            message = json.dumps(message)
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

def _init_mqtt(self: MLWrapper):
    """ Initialises a mock mqtt client """
    self.client = MockMqttClient(self.logger)
    self.client.on_message = self._react_to_message

def create_new_init(original_init: callable):
    print(inspect.getsource(original_init))
    def _new_init_(self: MLWrapper, **kwargs):
        self.out_messages: List[OutgoingMessage] = list()
        print(self.__class__)
        print("Running")
        if "outgoing_message_is_temporary" not in kwargs:
            kwargs["outgoing_message_is_temporary"] = True
        try:
            original_init(self, **kwargs)
        except TypeError:
            original_init(self)
        self.logger_ = logging.getLogger("MOCK")
        self.logger_.setLevel(logging.DEBUG)
        self.logger.debug(type(self))
        self.logger.debug(self.config)
    return _new_init_


def create_resolve_result(original_resolve_function: callable):
    async def resolve_result_data(self: MLWrapper, result: Union[pd.DataFrame, List[pd.DataFrame], dict],
            out_message: OutgoingMessage,
        ) -> OutgoingMessage:
        out_message = await original_resolve_function(self, result, out_message)
        self.logger.info("I saved the result in out_messages for you")
        self.out_messages.append(out_message)
        return out_message
    return resolve_result_data


def create_mock_tool(MLTOOL: Type[MLWrapper]) -> Type[MLWrapper]:
    """
    Creates a mock version of your ML Tool
    """
    MLTOOL.__init__ = create_new_init(MLTOOL.__init__)
    MLTOOL._init_mqtt = _init_mqtt
    MLTOOL.resolve_result_data = create_resolve_result(MLTOOL.resolve_result_data)
    return MLTOOL
