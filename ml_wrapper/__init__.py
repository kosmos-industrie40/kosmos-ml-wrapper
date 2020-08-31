"""
Wrapper module for ML applications.
Aims to alleviate ML engineers of extensive administrative overhead
and configuration for MQTT messaging.
"""

import logging
import abc
import sys
from multiprocessing.pool import ThreadPool
import os
import json
from typing import Union, List
import traceback
from enum import Enum
import pandas as pd
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage, Client
from iniparser import Config

from .convert_data import retrieve_data, resolve_data

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


class ResultType(Enum):
    """
    Enum for the result Types of an analyse
    """

    TEXT = "text"
    TIME_SERIES = "time_series"
    MULTIPLE_TIME_SERIES = "multiple_time_series"


class MLWrapper(abc.ABC):
    """
    The MLWrapper class handles all administrative overhead regarding
    incoming and outgoing MQTT messages.

    An instance of this class needs to be provided with information
    about incoming and outgoing topics through a config.ini file.
    Besides, the type of the analysis result
    (either of "text", "time_series", or "multiple_time_series")
    should be given upon instantiation (defaults to "time_series").

    As an ML Engineer, a child class of MLWrapper needs to be implemented
    and the run() method needs to be overwritten.
    Here, the main workload of your ML analysis module should be implemented.

    The arguments of the run() method need to conform
    to the outputs of retreive_payload_data() and to the inputs
    of the resolve_payload_data() method.
    The latter two can also be customized as needed.
    (The current implementation takes the sensor or analysis data from an
    incoming message, converts them to a pandas dataframe and passes is to
    the run() method.)

    In simplified terms, the main analysis workflow looks like the following:
    retrieved_data = self.retrieve_payload_data()
    result = self.run(*retrieved_data)
    message_payload = self.resolve_payload_data(result).

    In the main program, self.start() shall be used to start an
    infinite loop and react to incoming MQTT messages.
    """

    def __init__(
        self,
        result_type: ResultType = ResultType.TIME_SERIES,
        log_level=logging.INFO,
        logger_name=None,
    ):
        """
        Constructor of ML Wrapper.
        :param result_type: optional
        :param log_level: optional from logging enum (e.g. logging.INFO)
        :param logger_name: optional name of the logger
        """
        assert result_type.value in ["text", "time_series", "multiple_time_series",], (
            "Resulttype needs to be either of 'text', 'time_series', or"
            " 'multiple_time_series'."
        )
        self.resulttype = result_type
        self.config = Config(mode="all_allowed").scan(FILE_DIR, True).read()
        self.logger_ = logging.getLogger(logger_name or __name__)
        if not self.logger_.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s\t%(levelname)-10s"
                    " %(processName)s\t%(name)s:\t%(message)s"
                )
            )
            self.logger_.addHandler(handler)
        self.logger_.propagate = False
        self.logger.debug("The config is: %s", str(self.config.config_rendered))
        self.config = self.config.config_rendered
        self.client = None
        self.thread_pool = ThreadPool(
            int(self.config["config"]["threading"]["pool_num"])
        )
        self.thread_pool.daemon = True
        self.async_result = None
        self._init_mqtt()
        self.client.on_message = self._react_to_message
        self._subscribe()

    @property
    def logger(self):
        """
        Returns the logger instance
        """
        return self.logger_

    def _init_mqtt(self):
        """ Initialise the mqtt client """
        self.client = mqtt.Client()
        self.client.connect(
            self.config["config"]["mqtt"]["host"],
            port=int(self.config["config"]["mqtt"]["port"]),
        )

    def _subscribe(self):
        """ Subscribe the client to the config/env topic """
        self.client.subscribe(
            self.config["config"]["messaging"]["request_topic"],
            qos=int(self.config["config"]["messaging"]["qos"]),
        )
        self.logger.info(
            "Subscribed to topic\t %s",
            self.config["config"]["messaging"]["request_topic"],
        )

    def start(self):
        """
        Start an infinite loop to listen to MQTT messages.
        """
        self.client.loop_forever()

    # pylint: disable=no-self-use
    # Could ppotentially be reimplemented by user, and can then gain self-use
    def prompt(self, result):
        """
        Callback function for successful execution of run().
        """
        if result is not None:
            self.logger.debug("Finished thread")

    def error_prompt(self, err):
        """
        Callback function for erroneous execution of run().
        """
        self.logger.error("There was an error while calling the run() method.")
        self.logger.error(err)
        self.thread_pool.terminate()
        self.thread_pool = ThreadPool(
            int(self.config["config"]["threading"]["pool_num"])
        )
        self.async_result = None
        traceback.print_exception(type(err), err, err.__traceback__)
        raise type(err)(err)

    # client and user_data are expected arguments by mqtt client
    # pylint: disable=unused-argument
    def _react_to_message(
        self, client: Client, user_data: Union[None, str], message: MQTTMessage
    ) -> Union[str, pd.DataFrame]:
        """ This method is the entry point when a message is received. """
        self.logger.debug("Message received: %s", format(str(message.payload)))
        try:
            retrieved_data = self.retrieve_payload_data(message.topic, message.payload)
        except ValueError as e:
            self.logger.error(e)
            return
        self.logger.debug("Start the threaded run of the ML Tool")
        self.async_result = self.thread_pool.apply_async(
            self._run,
            retrieved_data,
            callback=self.prompt,
            error_callback=self.error_prompt,
        )

        self.logger.debug("closed and joined pool")

    # Can be reimplemented by user, and can then gain self-use
    def retrieve_payload_data(
        self, topic: str, payload: str
    ) -> (Union[pd.DataFrame, None], list, list, Union[dict, list, None], str, str):
        """
        Convert the data contained in an MQTT message payload
        to a usable format for ML applications.

        :param topic: MQTT message topic as a string
        :param payload: MQTT message payload as a string
        :returns dataframe: Payload results converted to Dataframe
        :return columns: Specification about column types and names
        :return data: Data from payload in list-representation
        :return metadata: List of dictionaries containing metadata about
            the data and data acquisition
        :return timestamp: Timestamp the trigger message
        :return topic: MQTT message topic as a string
        """
        dataframe, columns, data, metadada, timestamp = retrieve_data(payload)
        return dataframe, columns, data, metadada, timestamp, topic

    # Can be reimplemented by user, and can then gain self-use
    def resolve_result_data(
        self, data: Union[list, pd.DataFrame, dict], resulttype: ResultType
    ) -> dict:
        """
        Formats the result from the analysis workflow so that it is
        usable as json payload.

        TODO: Analysis output for 'text' resulttype still not entirely clear. Need
        to discuss the data structure of such a function's returned data structure.

        :param data: The data to be resolved
        :param resulttype: The type of the return value of the analysis function.
            Can either be "text", "time_series", or "multiple_time_series".
            (TODO: Need to define correct structure of "text" type.)
        :return schema: Dictionary containing the analysis result in a structure
            that conforms to the defined json schema.
        """
        self.logger.debug("Resolving data")
        self.logger.debug(str(data))
        schema = resolve_data(data, resulttype.value)
        return schema

    def _run(self, *args):
        """
        Wrapper around the actual run method.
        Executes run() and passes its result to and MQTT message.
        """
        self.logger.debug("Start ML tool...")
        result = self.run(*args)
        self.logger.debug("End ML tool")
        payload = self._publish_result_message(result)
        return payload

    def _publish_result_message(self, payload):
        """ This method is called when the run process is done and the result is to be published """
        payload = self.resolve_result_data(payload, self.resulttype)
        self.client.publish(
            self.config["config"]["messaging"]["result_topic"],
            payload=json.dumps(payload),
        )
        return payload

    @abc.abstractmethod
    def run(
        self,
        dataframe: Union[str, pd.DataFrame, None] = None,
        columns: List[dict] = None,
        data: List[dict] = None,
        metadada: Union[List[dict], None] = None,
        timestamp: str = None,
        topic: str = None,
    ) -> Union[str, pd.DataFrame]:
        """
        Interface for ML function.

        Arguments need to conform to the outputs of
        self.retrieve_payload_data().
        Likewise, outputs need to conform to the arguments of
        self.resolve_payload_data().

        In simplified terms, this will be called like the following:
        retrieved_data = self.retrieve_payload_data()
        result = self.run(*retrieved_data)
        message_payload = self.resolve_payload_data(result).

        :param dataframe: Payload data converted to Dataframe
        :param columns: Specification about column types and names
        :param data: Data from payload in list-representation
        :param metadata: List of dictionaries containing metadata about
            the data and data acquisition
        :param timestamp: Timestamp of the trigger message
        :param topic: Topic of the trigger message
        :return data: Analysis result data
        :return resulttype: Type of the analysis result. Enum ResultType is used
        """
        self.logger.warning("This method needs to be implemented!")
        return NotImplementedError
