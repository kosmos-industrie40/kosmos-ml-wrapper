"""
Wrapper module for ML applications.
Aims to alleviate ML engineers of extensive administrative overhead
and configuration for MQTT messaging.
"""

import logging
import abc
import re
import sys
from multiprocessing.pool import ThreadPool
import os
from typing import Union, List
import traceback
import pandas as pd
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage, Client
from iniparser import Config

from .exceptions import (
    EmptyResult,
    InvalidType,
    NotInitialized,
    NonSchemaConformJsonPayload,
)
from .helper import topic_splitter
from .messaging import IncomingMessage, OutgoingMessage
from .result_type import ResultType

from .log_level import LOG_LEVEL

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


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
        log_level=LOG_LEVEL,
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
        self.result_type = result_type
        self._config = Config(mode="all_allowed").scan(FILE_DIR, True).read()
        self.logger_ = logging.getLogger(logger_name or __name__)
        if not self.logger_.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s\t%(filename)-20sline %(lineno)-4d %(levelname)s"
                    ": \t%(message)s"
                )
            )
            self.logger_.addHandler(handler)
        self.logger_.propagate = False
        self.logger.debug("The config is: %s", str(self._config.config_rendered))
        self.config = self._config.config_rendered
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
        topics = topic_splitter(self.config["config"]["messaging"]["request_topic"])
        for topic in topics:
            self.client.subscribe(
                topic=topic,
                qos=int(self.config["config"]["messaging"]["qos"]),
            )
            self.logger.info(
                "Subscribed to topic\t %s",
                topic,
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
    # pylint: disable=unused-argument,broad-except
    def _react_to_message(
        self, client: Client, user_data: Union[None, str], message: MQTTMessage
    ):
        """ This method is the entry point when a message is received. """
        self.logger.debug("Message received: %s", format(str(message.payload)))
        in_message = IncomingMessage(logger=self.logger)
        self.logger.debug("Message is now referenced by %s", in_message.mid)
        try:
            self.logger.info(in_message)
            in_message.mqtt_message = message
            self.logger.info(in_message)
        except (EmptyResult, InvalidType, NonSchemaConformJsonPayload) as error:
            self.logger.error("%s:\n%s", error.__class__.__name__, error)
            raise error from error
        except Exception as error:
            self.logger.error(
                "The exception %s has to be handled!\n%s",
                error.__class__.__name__,
                error,
            )
            raise error from error
        self.logger.debug("Start the threaded run of the ML Tool")
        self.async_result = self.thread_pool.apply_async(
            self._run,
            [in_message],
            callback=self.prompt,
            error_callback=self.error_prompt,
        )

        self.logger.debug("closed and joined pool")

    # Can be reimplemented by user, and can then gain self-use
    def retrieve_payload_data(self, in_message: IncomingMessage) -> IncomingMessage:
        """
        This method allows you to retrieve additional information or to temper with the
        automatically parsed information in the IncomingMessage object.

        The recomended way of adding information is to use the in_message's field
        in_message.custom_information_field to store your own information and pass it to the
        other functions.

        @param in_message: IncomingMessage
        @return: IncomingMessage
        """
        self.logger.debug(in_message.id_ref)
        self.logger.debug("Retrieve data")
        return in_message

    # Can be reimplemented by user, and can then gain self-use
    def resolve_result_data(
        self,
        result: Union[pd.DataFrame, List[pd.DataFrame], dict],
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        """
        This method automatically resolves the data results into a valid payload. If your case
        is not covered by the standard cases, we highly recommend to discuss to include this into
        the ML Wrapper. If you need to update some fields manually, you can do this here.

        This function has to return an OutgoingMessage object. After this method, only the
        out_message.payload getter is called. So if you want to change or temper with the
        payload, you can set the out_message's payload here. However, be aware that only
        valid jsons will be accepted to write to the payload.

        If you want to overwrite this method we encourage you to use the following procedure as
        example for the text result case:
        .. highlight:: python
        .. code-block:: python

            out_message = super().resolve_result_data(result, out_message)
            payload_dict = out_message.payload_as_json_dict
            payload_dict["results"]["total"] = "tempered result"
            out_message.payload = payload_dict

        This way you will only change the dictionary where required and make sure you have a
        valid json.

        @param result: result of the run method
        @param out_message: OutgoingMessage
        @return: OutgoingMessage
        """
        self.logger.debug(out_message.in_message.id_ref)
        self.logger.debug("Resolving data")
        out_message.set_results(result, result_type=self.result_type)
        return out_message

    def _run(self, in_message: IncomingMessage) -> OutgoingMessage:
        """
        Wrapper around the actual run method.
        Executes run() and passes its result to a MQTT message.
        """
        self.logger.debug(in_message.id_ref)
        self.logger.debug("Start ML tool...")
        out_message = OutgoingMessage(
            self.retrieve_payload_data(in_message),
            base_topic=self._config.get(
                "messaging", "base_result_topic", default="kosmos/analyses/"
            ),
        )
        result = self.run(out_message)
        if not any([isinstance(result, dtype) for dtype in [pd.DataFrame, list, dict]]):
            raise TypeError(
                "The run method has to provide a DataFrame, a list of DataFrames or a dictionary"
            )
        self.logger.debug("End ML tool")
        out_message = self.resolve_result_data(result, out_message)
        try:
            out_message.payload
        except NotInitialized as error:
            self.logger.error(error)
            self.logger.error(
                "You need to specify the payload. If you overwrite the "
                "resolve_result_data method, please make sure to provide "
                "the payload manually!"
            )
            return None
        out_message = self._publish_result_message(out_message)
        return out_message

    def _publish_result_message(
        self,
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        """This method is called when the run process is done and the result is to be published
        @param out_message: OutgoingMessage
        @return: OutgoingMessage
        """
        self.logger.debug(out_message.in_message.id_ref)
        self.logger.debug("Publish the result to %s", out_message.topic)
        payload = out_message.payload
        if re.match(r"/?kosmos/analyses/[^/]+", out_message.topic) is None:
            self.logger.warning(
                "You are using an undefined topic %s. Please consider either correcting "
                "your publishing topic or open an issue for the ML Wrapper to include "
                "the new topic into the logic.",
                out_message.topic,
            )
        self.client.publish(
            topic=out_message.topic,
            payload=payload,
        )
        return out_message

    @abc.abstractmethod
    def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """
        The run method executes your actual ML Logic.

        Here you can start your calculations/functions and collect the results.
        The out_message object is the one that should be returned. You will be able to pass
        some standard results using the OutgoingMessage Class directly, or if you need to specify
        the outgoing payload more, you can overwrite the resolve_result_data method.

        Please note, that you can access the incomingMessage object with out_message.in_message.

        @param out_message: OutgoingMessage
        @return: OutgoingMessage
        """
        self.logger.warning("This method needs to be implemented!")
        return NotImplementedError
