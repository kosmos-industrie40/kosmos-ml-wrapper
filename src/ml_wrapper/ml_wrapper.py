"""
Wrapper module for ML applications.
Aims to alleviate ML engineers of extensive administrative overhead
and configuration for MQTT messaging.
"""

import abc
import asyncio
import logging
import os
import re
import signal
import sys
import time
import warnings
from typing import List, Union

import paho.mqtt.client as mqtt
import pandas as pd
import uvicorn
from iniparser import Config
from paho.mqtt.client import Client, MQTTMessage

from .messaging import IncomingMessage, MessageType, OutgoingMessage
from .messaging.state_message import StateMessage, ToolState
from .misc import (
    ConfigNotValid,
    EmptyResult,
    handle_exception,
    InvalidType,
    LOG_LEVEL,
    NonSchemaConformJsonPayload,
    NotInitialized,
    ResultType,
    topic_splitter,
    WrongMessageType,
)
from .misc.fastAPI_server import app, Server
from .misc.prometheus import state as prometheus_state, message_issue_counter

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


# pylint: disable=too-many-instance-attributes
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
        only_react_to_message_type: MessageType = None,
        only_react_to_previous_result_types: Union[None, List[ResultType]] = None,
        outgoing_message_is_temporary: bool = None,
        client=None,
        async_loop=None,
    ):
        """
        Constructor of ML Wrapper.
        :param result_type: optional
        :param log_level: optional from logging enum (e.g. logging.INFO)
        :param logger_name: optional name of the logger
        :param only_react_to_message_type: optional to set the reaction type
        :param only_react_to_previous_result_types: optional to set previous result_type required
        :param outgoing_message_is_temporary: Required to define whether your result should be
        stored (False) or just used for following steps (True)
        """
        # Handle result_type
        assert result_type.value in ["text", "time_series", "multiple_time_series",], (
            "Resulttype needs to be either of 'text', 'time_series', or"
            " 'multiple_time_series'."
        )
        self.result_type = result_type

        self._config = Config(mode="all_allowed").scan(FILE_DIR, True).read()

        # Handle message type that is accepted
        assert only_react_to_message_type is None or isinstance(
            only_react_to_message_type, MessageType
        ), "only_react_to_message_type can only be None or a MessageType"
        self._only_react_to_message_type = only_react_to_message_type

        # Handle result types to react to
        assert only_react_to_previous_result_types is None or (
            isinstance(only_react_to_previous_result_types, list)
            and all(
                isinstance(constraint, ResultType)
                for constraint in only_react_to_previous_result_types
            )
        ), "only_react_to_previous_result_types can only be None or a list of ResultType"
        self._only_react_to_previous_result_types = only_react_to_previous_result_types

        # Handle outgoing persistence settings
        assert outgoing_message_is_temporary is not None and isinstance(
            outgoing_message_is_temporary, bool
        ), (
            "outgoing_message_is_temporary has to be set by the "
            "ML Wrapper implementing tool and hast to be boolean type!"
        )
        self._outgoing_message_is_temporary = outgoing_message_is_temporary

        # Initialize logger
        self.logger_ = logging.getLogger(logger_name or __name__)
        if not self.logger_.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s\t%(name)s\t%(filename)-20s "
                    "%(funcName)-20s %(lineno)-4d %(levelname)s"
                    ": \t%(message)s"
                )
            )
            self.logger_.addHandler(handler)
        self.logger_.propagate = False
        self.logger.debug("The config is: %s", str(self._config.config_rendered))

        # Render and set config at beginning
        self.config = self._config.config_rendered
        self._check_config_sanity()

        # Init the mqtt and thread specifics
        self.client = client
        self.async_loop = async_loop
        self.async_loop_policy = asyncio.get_event_loop_policy()
        self.state_topic = self._config.get("status_topic", default="kosmos/status")

        self.state: StateMessage = None

        # Miscellaneous
        self.raise_exceptions = (
            self._config.get("raise_excpetions", default="False").lower() != "false"
        )
        self._save_exit = False
        self.server: Server = None

    def start_up_components(self) -> None:
        """
        This method will connect the initialise the mqtt
        client and start up all components required.
        """
        self.logger.info("Starting all components...")

        # Prometheus and asgi server
        self.logger.info("Starting server and prometheus")
        config = uvicorn.Config(
            app,
            host=self._config.get("prometheus_serve_host", default="0.0.0.0"),
            port=int(self._config.get("prometheus_serve_port", default="8020")),
        )
        self.server = Server(config=config)
        self.server.t_start()

        prometheus_state.state(ToolState.STARTING.value)
        self.logger.info("Prometheus running")

        # Async loop setup
        self.logger.info("Starting async loop")
        self.async_loop = self.async_loop_policy.new_event_loop()
        asyncio.set_event_loop(self.async_loop)
        self.async_loop.close_ = self.async_loop.close
        self.async_loop.close = lambda: None
        self.logger.info("Asyncloop running")

        # MQTT
        self.logger.info("Initialize MQTT connection")
        self._init_mqtt()
        self.client.loop_start()
        self._wait_for_connection()
        self._subscribe()
        self.state = StateMessage(
            client=self.client,
            topic=self.state_topic,
            logger=self.logger,
            from_=self.config["config"]["model"]["from"],
        )
        self.logger.info("MQTT running")
        self.state.state = ToolState.ALIVE

        # SIG commands
        self.logger.info("Register SIG commands for save shutdown")
        for signal_ in self._config.get("sigterm_calls", default="SIGINT").split(","):
            signal_ = signal_.strip()
            if hasattr(signal, signal_):
                self.logger.info("Register %s as save exit call", signal_)
                signal.signal(getattr(signal, signal_), self.save_exit)

        self.logger.info("... all components started")

        # Start looping
        self.loop_forever()

    def _wait_for_connection(self):
        """
        This function pauses the main thread until the client is connected
        """
        sleep_time = 1
        sleep_counter = 0
        while not self.client.is_connected():
            time.sleep(sleep_time)
            self.logger.debug("MQTT connection retry. Counter: %d", sleep_counter)
            sleep_counter += 1

    def tear_down_components(self) -> None:
        """
        This method will tear down all components, like the mqtt client
        """
        self.logger.info("Tearing down all components...")
        self.state.state = ToolState.SHUTTING_DOWN
        self.logger.info("Tearing down MQTT connection...")
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info("Tearing down Async loop...")
        self.async_loop.close_()
        self.logger.info("Tearing down server...")
        self.server.t_end()
        self.logger.info("... all components torn down")

    # pylint: disable=unused-argument
    def save_exit(self, *args, **kwargs):
        """
        Closes the forever loop
        """
        self.logger.info("Application was told to shut down. Invoking save exit")
        self._save_exit = True

    def loop_forever(self):
        """
        This loop will run infinitively and keep the main thread alive.
        """
        while not self._save_exit:
            time.sleep(0.1)

    def __enter__(self):
        """
        Controlled setup
        """
        self.start_up_components()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tear_down_components()

    def _check_config_sanity(self):
        """Checks the sanity of the config file at creation time"""
        assert (
            "url" in self.config["config"]["model"]
        ), "url needs to be set in the configuration file"
        assert (
            "tag" in self.config["config"]["model"]
        ), "tag needs to be set in the configuration file"
        assert (
            "from" in self.config["config"]["model"]
        ), "from needs to be set in the configuration file"
        for field in ["url", "tag", "from"]:
            current = self.config["config"]["model"][field]
            if len(current) <= 0:
                raise ConfigNotValid(
                    "The field {} has to be set either in the configuration "
                    "file of the MLWrapper, or with the help of the according "
                    "environment variable. You can find all the environment variables in the "
                    "env_ml_wrapper.md file.\nAvailable environment variables are:\n{}".format(
                        field, self._config.environment_variables
                    )
                )

    @property
    def logger(self):
        """
        Returns the logger instance
        """
        return self.logger_

    def _init_mqtt(self):
        """Initialise the mqtt client"""
        self.client = mqtt.Client()
        self.client.connect_async(
            self.config["config"]["mqtt"]["host"],
            port=int(self.config["config"]["mqtt"]["port"]),
        )
        self.client.on_message = self._react_to_message

    # Pylint misclassifies .get of config object as no member.
    # This is wrong and therefore disabled
    # pylint: disable=no-member
    def _get_topics(self):
        topics = topic_splitter(self.config["config"]["messaging"]["request_topic"])
        base = self._config.get(
            "messaging", "analytic_base_url", default="kosmos/analytics/"
        )
        model_url = self._config.get("model", "url")
        model_tag = self._config.get("model", "tag")
        topics.append(f"{base}/{model_url}/{model_tag}".replace("//", "/"))
        return topics

    def _subscribe(self):
        topics = self._get_topics()
        for topic in topics:
            (response, _) = self.client.subscribe(
                topic=topic,
                qos=int(self.config["config"]["messaging"]["qos"]),
            )
            if response != 0:
                self.logger.error("Error subscribing to topic\t %s", topic)
            else:
                self.logger.info("Subscribed to topic\t %s", topic)

    # DEPRECATED: This method is deprecated!
    def start(self):
        """
        Deprecated
        Start an infinite loop to listen to MQTT messages.
        """
        warnings.warn(
            "Start is deprecated and updated to new behaviour of set up. "
            "Please change to 'with Tool() as tool:' style for better handling"
        )
        self.start_up_components()

    def _check_message_requirements(self, message: IncomingMessage):
        if self._only_react_to_message_type is None:
            return
        if message.message_type != self._only_react_to_message_type:
            raise WrongMessageType(
                "The message I received is of type {} but the "
                "tool is only reacting to type {}".format(
                    message.message_type.value, self._only_react_to_message_type.value
                )
            )
        if (
            message.message_type == MessageType.ANALYSES_RESULT
            and self._only_react_to_previous_result_types is not None
        ):
            if (
                message.analyses_message_type
                not in self._only_react_to_previous_result_types
            ):
                raise WrongMessageType(
                    "The message I received is a previously calculated analyse result. "
                    "However I require a message of type {}".format(
                        " or ".join(
                            list(
                                map(
                                    lambda x: x.value,
                                    self._only_react_to_previous_result_types,
                                )
                            )
                        )
                    )
                )
        return

    # client and user_data are expected arguments by mqtt client
    # Furthermore no exception should completely kill the tool
    # pylint: disable=unused-argument,broad-except
    def _react_to_message(
        self, client: Client, user_data: Union[None, str], message: MQTTMessage
    ):
        """This method is the entry point when a message is received."""
        self.logger.debug("Message received: %s", format(str(message.payload)))
        in_message = IncomingMessage(logger=self.logger)
        self.logger.debug("Message is now referenced by %s", in_message.mid)
        try:
            self.logger.debug(in_message)
            in_message.mqtt_message = message
            self._check_message_requirements(in_message)
        except (EmptyResult, InvalidType, NonSchemaConformJsonPayload) as error:
            self.logger.error("%s:\n%s", error.__class__.__name__, error)
            message_issue_counter.inc()
            handle_exception(
                exception=error,
                logger=self.logger,
                state=self.state,
                raise_further=self.raise_exceptions,
            )
            return
        except WrongMessageType as error:
            self.logger.error("%s: \n%s", WrongMessageType.__name__, error)
            handle_exception(
                exception=error,
                logger=self.logger,
                state=self.state,
                raise_further=False,
            )
            return
        except Exception as error:
            self.logger.error(
                "The exception %s has to be handled!\n%s",
                error.__class__.__name__,
                error,
            )
            handle_exception(
                exception=error,
                logger=self.logger,
                state=self.state,
                raise_further=self.raise_exceptions,
            )
            return
        self.logger.debug(
            "Start the async run of the ML Tool for message %s", in_message.mid
        )
        # Run sub task in save environment
        try:
            self.async_loop.run_until_complete(self._run(in_message))
        except Exception as error:
            self.logger.error(
                "The exception %s has to be handled!\n%s",
                error.__class__.__name__,
                error,
            )
            handle_exception(
                exception=error,
                logger=self.logger,
                state=self.state,
                raise_further=self.raise_exceptions,
            )
            return
        self.logger.debug("Finished tool for message %s", in_message.mid)

    # Can be reimplemented by user, and can then gain self-use
    async def retrieve_payload_data(
        self, in_message: IncomingMessage
    ) -> IncomingMessage:
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
    async def resolve_result_data(
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
        ::

            out_message = await super().resolve_result_data(result, out_message)
            body_dict = out_message.body_as_json_dict
            body_dict["results"]["total"] = "tempered result"
            out_message.body = body_dict
            return out_message

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

    async def _run(self, in_message: IncomingMessage) -> OutgoingMessage:
        """
        Wrapper around the actual run method.
        Executes run() and passes its result to a MQTT message.
        """
        self.logger.debug(in_message.id_ref)
        self.logger.debug("Start ML tool...")
        out_message = OutgoingMessage(
            await self.retrieve_payload_data(in_message),
            from_=self._config.get("model", "from"),
            model_tag=self._config.get("model", "tag"),
            model_url=self._config.get("model", "url"),
            base_topic=self._config.get(
                "messaging", "base_result_topic", default="kosmos/analyses/"
            ),
            is_temporary=self._outgoing_message_is_temporary,
            temporary_keyword=self._config.get(
                "messaging", "temporary_keyword", default="temporary"
            ),
        )
        result = await self.run(out_message)
        print(result)
        if not any(isinstance(result, dtype) for dtype in [pd.DataFrame, list, dict]):
            raise TypeError(
                "The run method has to provide a DataFrame, a list of DataFrames or a dictionary"
            )
        self.logger.debug("End ML tool")
        out_message = await self.resolve_result_data(result, out_message)
        try:
            out_message.body
        except NotInitialized as error:
            self.logger.error(error)
            self.logger.error(
                "You need to specify the payload. If you overwrite the "
                "resolve_result_data method, please make sure to provide "
                "the 'body' field of the payload manually!"
            )
            handle_exception(
                exception=error,
                logger=self.logger,
                state=self.state,
                raise_further=self.raise_exceptions,
            )
            return
        print(out_message.body)
        out_message = await self._publish_result_message(out_message)
        return out_message

    async def _publish_result_message(
        self,
        out_message: OutgoingMessage,
    ) -> OutgoingMessage:
        """This method is called when the run process is done and the result is to be published
        @param out_message: OutgoingMessage
        @return: OutgoingMessage
        """
        self.logger.debug(out_message.in_message.id_ref)
        self.logger.debug("Publish the result to %s", out_message.topic)
        if re.match(r"/?kosmos/analyses/[^/]+", out_message.topic) is None:
            self.logger.warning(
                "You are using an undefined topic %s. Please consider either correcting "
                "your publishing topic or open an issue for the ML Wrapper to include "
                "the new topic into the logic.",
                out_message.topic,
            )
        self.client.publish(
            topic=out_message.topic,
            payload=out_message.payload,
        )
        return out_message

    @abc.abstractmethod
    async def run(
        self, out_message: OutgoingMessage
    ) -> Union[pd.DataFrame, List[pd.DataFrame], dict]:
        """
        The run method executes your actual ML Logic.

        Here you can start your calculations/functions and collect the results.
        The result that you will return has to be of the type DataFrame, a list of DataFrames,
        or a dictionary, according to the json specifications. If you need to specify
        the outgoing payload more, you can overwrite the resolve_result_data method.

        Please note, that you can access the incomingMessage object with out_message.in_message.

        @param out_message: OutgoingMessage
        @return: pandas.DataFrame, List[pandas.DataFrame], or dict
        """
        self.logger.warning("This method needs to be implemented!")
        return NotImplementedError
