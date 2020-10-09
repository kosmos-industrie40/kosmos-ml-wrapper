"""
This provides a Messaging object which logic is used to pass on information between the stages of
the ML Wrapper Tool
"""
import datetime
import inspect
import json
import logging
import re
import uuid
from datetime import timezone
from json.decoder import JSONDecodeError
from typing import Union
import pandas as pd

from jsonschema import ValidationError
from paho.mqtt.client import MQTTMessage

from .message_type import MessageType
from .result_type import ResultType
from .json_validator import (
    validate_trigger,
    validate_formal_single,
)
from .helper import find_result_type
from .convert_data import (
    retrieve_sensor_update_data,
    retrieve_dataframe,
    resolve_data_frame,
)
from .exceptions import (
    NotInitialized,
    NonSchemaConformJsonPayload,
    NotYetRetrieved,
    InvalidType,
    EmptyResult,
    InvalidTopic,
)


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class IncomingMessage:
    """
    This class represents a Messaging object to pass on information between the stages of the
    ML Wrapper
    """

    def __init__(self, logger: logging.Logger):
        self._id = uuid.uuid4()
        self._model = None
        self._tag = None
        self._contract = None
        self._machine = None
        self._sensor = None
        self._topic = None
        self._payload = None
        self._mqtt_message = None
        self._message_type = None
        self._message_data_type = None
        self._retrieved_data = None
        self._columns = None
        self._data = None
        self._column_meta = None
        self._metadata = None
        self._timestamp = None
        self._received = (
            datetime.datetime.utcnow().astimezone(timezone.utc).isoformat(sep="T")
        )
        self.custom_information_field = None
        self.logger = logger

    @property
    def column_meta(self):
        """ Returns the protected property for column_meta """
        return self._column_meta

    @column_meta.setter
    def column_meta(self, new_value: dict):
        """
        Sets the protected property for column_meta
        :@param new_value: dict
        """
        assert isinstance(
            new_value, dict
        ), "The value to be set has to be of type dict, but received {}".format(
            type(new_value)
        )
        self._column_meta = new_value

    @column_meta.deleter
    def column_meta(self):
        """ Deletes the protected property for column_meta """
        del self._column_meta

    @property
    def mid(self):
        """The messages unique id"""
        return self._id

    @property
    def id_ref(self):
        """The id in a sentence"""
        return "Message id {}".format(self.mid)

    @property
    def received(self):
        """The timestamp, when the Message was received"""
        return self._received

    @property
    def sensor(self):
        """ The sensor of the triggering message """
        return self._sensor

    @property
    def model(self):
        """ The model of the triggering message """
        return self._model

    @property
    def machine(self):
        """ The machine of the triggering message """
        return self._machine

    @property
    def contract(self):
        """ The contract of the triggering message """
        return self._contract

    @property
    def message_type(self):
        """ Returns the retrieved message type """
        return self._message_type

    @property
    def retrieved_data(self):
        """ Returns the retrieved data from the message """
        return self._retrieved_data

    @property
    def columns(self):
        """ Returns the columns field from the message """
        return self._columns

    @property
    def data(self):
        """ Returns the data field from the message """
        return self._data

    @property
    def metadata(self):
        """ Returns the metadata field from the message """
        return self._metadata

    @property
    def timestamp(self):
        """ Returns the timestamp field from the message """
        return self._timestamp

    def _retrieve(self):
        """
        Convert the data contained in an MQTT message payload
        to a usable format for ML applications.
        """
        self.check_initialized()
        metadata = None
        retrieved_data = None
        columns = None
        data = None
        msg = self.payload["body"]
        timestamp = msg.get("timestamp")
        if self._message_type is MessageType.ANALYSES_Result:
            try:
                analyses_msg_type = ResultType.value2member_map()[msg.get("type")]
            except KeyError as error:
                raise InvalidType(error) from error
            self.analyses_message_type = analyses_msg_type
            if analyses_msg_type == ResultType.TIME_SERIES:
                results = msg.get("results")
                if results is None:
                    raise EmptyResult("The result of a message cannot be empty")
                retrieved_data, columns, data = retrieve_dataframe(results)
            elif analyses_msg_type == ResultType.TEXT:
                results = msg.get("results")
                if results is None:
                    raise EmptyResult("The result of a message cannot be empty")
                retrieved_data = results
            elif analyses_msg_type == ResultType.MULTIPLE_TIME_SERIES:
                results = msg.get("results")
                if results is None:
                    raise EmptyResult("The result of a message cannot be empty")
                columns = list()
                retrieved_data = list()
                data = list()
                for result in results:
                    data_frame_, columns_, data_ = retrieve_dataframe(result)
                    columns.append(columns_)
                    retrieved_data.append(data_frame_)
                    data.append(data_)
            else:
                raise InvalidType(
                    "This message type {} has not been implemented".format(
                        analyses_msg_type
                    )
                )
        elif self._message_type is MessageType.SENSOR_UPDATE:
            (
                retrieved_data,
                columns,
                data,
                metadata,
                self.column_meta,
            ) = retrieve_sensor_update_data(msg)
        else:
            raise NotImplementedError(
                "The type {} is not yet implemented".format(self._message_type)
            )
        self._retrieved_data = retrieved_data
        self._columns = columns
        self._data = data
        self._metadata = metadata
        self._timestamp = timestamp

    @property
    def is_retrieved(self):
        """
        Returns true, if all fields have been set
        return: bool
        """
        return any(
            [
                field is not None
                for field in [
                    self._retrieved_data,
                    self._columns,
                    self._data,
                ]
            ]
        )

    def check_retrieved(self):
        """
        Raises NotYetRetrieved, if one required field is not yet set
        """
        if not self.is_retrieved:
            fields = [self._retrieved_data, self._columns, self._data, self._timestamp]
            raise NotYetRetrieved(
                "The fields {} are not retrieved yet".format(
                    [field for field in fields if field is None]
                )
            )

    @property
    def is_initialized(self):
        """
        Returns true iff the topic and the payload are not None
        """
        return self._payload is not None and self._topic is not None

    def check_initialized(self):
        """
        Checks the initialized status and raises an Exception if not properly set
        """
        if not self.is_initialized:
            raise NotInitialized(
                "The Information/Messaging object has not been initialized (properly). Please "
                "initialize by using \n"
                "information.mqtt_message = <MQTTMessage>"
            )

    @property
    def analyses_message_type(self):
        """ Returns the protected property for message_data_type """
        return self._message_data_type

    @analyses_message_type.setter
    def analyses_message_type(self, new_value: ResultType):
        """
        Sets the protected property for message_data_type
        :param new_value: ResultType
        """
        assert isinstance(
            new_value, ResultType
        ), "The value to be set has to be of type ResultType, but received {}".format(
            type(new_value)
        )
        self._message_data_type = new_value

    @analyses_message_type.deleter
    def analyses_message_type(self):
        """ Deletes the protected property for message_data_type """
        del self._message_data_type

    @property
    def mqtt_message(self):
        """ Returns the protected property for mqtt_message """
        return self._mqtt_message

    @mqtt_message.setter
    def mqtt_message(self, new_value: MQTTMessage):
        """
        Sets the protected property for mqtt_message
        :param new_value: MQTTMessage
        """
        self.logger.debug("Enter setter of mqtt_message")
        assert (
            inspect.isclass(new_value) and issubclass(new_value, MQTTMessage)
        ) or isinstance(
            new_value, MQTTMessage
        ), "The value to be set has to be of type MQTTMessage, but received {}".format(
            type(new_value)
        )
        self._mqtt_message = new_value
        self._initialize_with_message()
        self._retrieve()
        self.logger.debug("Exit setter of mqtt_message")

    @mqtt_message.deleter
    def mqtt_message(self):
        """ Deletes the protected property for mqtt_message """
        del self._mqtt_message

    def _initialize_with_message(self):
        self.logger.debug("Enter initialize with message")
        assert (
            self._mqtt_message is not None
        ), "MQTT Message needs to be set prior to this method"
        self.payload = self.mqtt_message.payload
        self.topic = self.mqtt_message.topic
        self.logger.debug("Exit initialize with message")

    @property
    def payload(self):
        """ Returns the protected property for payload """
        return self._payload

    @payload.setter
    def payload(self, new_value: str):
        """
        Sets the protected property for payload
        :param new_value: json string
        """
        self.logger.debug("Enter setter of payload")
        try:
            payload = json.loads(new_value)
        except JSONDecodeError as error:
            raise error from error
        type_ = None
        if "body" not in payload:
            self.logger.error("The 'body' key is required in payload")
            raise KeyError("The 'body' key is required in payload")
        try:
            type_ = payload["body"]["type"]
        except KeyError as error:
            raise KeyError("The 'type' keyword is required in the payload") from error
        try:
            message_type = MessageType.value2member_map()[type_]
        except KeyError as error:
            raise NonSchemaConformJsonPayload(
                "Wrong Message type used\n{}\n{}".format(
                    error,
                    "You cannot use {} as type in the root level here. "
                    "I only accept ml-formal.json conform messages".format(type_),
                )
            ) from error
        try:
            validate_trigger(payload)
            # validate_formal(payload["payload"])
        except NonSchemaConformJsonPayload as error:
            raise error from error
        self._machine = payload["body"].get("machine")
        self._sensor = payload["body"].get("sensor")
        self._contract = payload["body"].get("contract")
        self._message_type = message_type
        self._payload = payload["body"].get("payload")
        self.logger.debug("Exit setter of payload")

    @payload.deleter
    def payload(self):
        """ Deletes the protected property for payload """
        del self._payload

    @property
    def topic(self):
        """ Returns the protected property for topic """
        return self._topic

    @topic.setter
    def topic(self, new_value: Union[str, bytes]):
        """
        Sets the protected property for topic
        :param new_value:
        """
        self.logger.debug("Setting topic with %s", new_value)
        new_value = (
            str(new_value, "utf-8") if isinstance(new_value, bytes) else new_value
        )
        if re.match("/?kosmos/analytics/[^/]+/[^/]+", new_value) is None:
            raise InvalidTopic(
                "Topic doesn't conform to the trigger "
                "topic kosmos/analystics/<model url>/<model tag>:\n{}".format(new_value)
            )
        regex_search = re.search(
            "/?kosmos/analytics/([^/]+)/([^/]+)/?", new_value, re.IGNORECASE
        )
        if not regex_search:
            raise InvalidTopic("The topic {} couldn't be parsed".format(new_value))
        self._model = regex_search.group(1)
        self._tag = regex_search.group(2)
        self._topic = new_value

    @topic.deleter
    def topic(self):
        """ Deletes the protected property for topic """
        del self._topic


class OutgoingMessage:
    """
    Outgoing Message object
    """

    def __init__(
        self,
        in_message: IncomingMessage,
        from_: str = None,
        model_url: str = None,
        model_tag: str = None,
        base_topic: str = "kosmos/analyses/",
        is_temporary: bool = True,
        temporary_keyword: str = None,
    ):
        self._body = None
        self.in_message = in_message
        self._base_topic = base_topic
        self.is_temporary = is_temporary
        self.logger = self.in_message.logger
        self._result = None
        self._result_type = None
        assert (
            temporary_keyword is not None
        ), "The variable temporary_keyword has to be set"
        assert from_ is not None, "The variable from_ has to be set"
        assert model_url is not None, "The variable model_url has to be set"
        assert model_tag is not None, "The variable model_tag has to be set"
        self.temporary_keyword = temporary_keyword
        self.from_ = from_
        self.model_url = model_url
        self.model_tag = model_tag

    @property
    def topic(self) -> str:
        """
        Calculates the topic to which the ml wrapper publishes with the contract ID from the
        IncomingMessage.
        @return: str
        """
        topic = "{}/{}".format(self._base_topic, self.in_message.contract).replace(
            "//", "/"
        )
        if self.is_temporary:
            topic += ("/" + self.temporary_keyword).replace("//", "/")
        self.logger.debug("Calculated topic is %s", topic)
        return topic

    @property
    def payload_as_json_dict(self) -> dict:
        """
        Returns the calculated payload string as a json dictionary
        @return: dict
        """
        return json.loads(self.payload)

    @staticmethod
    def _sign_body():
        return "This has to be done"

    @staticmethod
    def _make_payload_dict(body: dict) -> dict:
        return {"body": body, "signature": ""}

    @property
    def payload(self) -> str:
        """ Returns the resulting payload as string """
        dict_ = self._make_payload_dict(self._body)
        dict_["signature"] = self._sign_body()
        return json.dumps(dict_)

    @property
    def body(self) -> str:
        """ Returns the protected property for payload """
        if self._body is None:
            raise NotInitialized(
                "The body of the outgoing message has to be set. "
                "You can either use the set_results method or set the "
                "field body directly."
            )
        return self._body

    @property
    def body_as_json_dict(self) -> dict:
        """ Returns the message field body as dictionary """
        return json.loads(self.body)

    @body.setter
    def body(self, new_value: Union[str, dict]):
        """
        Sets the protected property for payload
        :@param new_value: str
        """
        assert isinstance(
            new_value, (str, dict)
        ), "The value to be set has to be of type str or dict, but received {}".format(
            type(new_value)
        )
        if isinstance(new_value, dict):
            new_value = json.dumps(new_value)
        try:
            validate_formal_single(
                json.dumps(self._make_payload_dict(json.loads(new_value)))
            )
        except ValidationError as error:
            raise NonSchemaConformJsonPayload(
                "This payload cannot be set as outgoing message. "
                "It is not schema conform to analyses-formal.json.\n"
                "I received the json {}.\n Validation Error:\n{}".format(
                    new_value, error.message
                )
            ) from error
        self._body = new_value

    @body.deleter
    def body(self):
        """ Deletes the protected property for payload """
        del self._body

    def set_results(
        self, result: Union[pd.DataFrame, list, dict], result_type: ResultType = None
    ):
        """
        This method needs to be called before resolving data. This method will transform your data
        into the schema conform json results.
        @param result: DataFrame, list of DataFrames or dictionary
        @param result_type: ResultType
        """
        if result_type is None:
            self.logger.warning(
                "It is not recommended to leave the result_type unset. However, we"
                " will try to parse the proper result type."
            )
            result_type = find_result_type(result)
            if result_type is None:
                raise ValueError(
                    "The given results are not parsable. Please set the result_type"
                    " explicitly."
                )
            self.logger.info("The result type was detected as %s", result_type)
        assert isinstance(
            result_type, ResultType
        ), "I can only handle ResultType for the result_type"
        resolved = dict()
        resolved["type"] = result_type.value

        # Derive ml tool specific values
        resolved["from"] = self.from_
        resolved["model"] = dict(
            url=self.model_url,
            tag=self.model_tag,
        )
        resolved["calculated"] = dict(
            message=dict(
                machine=self.in_message.machine, sensor=self.in_message.sensor
            ),
            received=self.in_message.received,
        )

        if result_type == ResultType.TIME_SERIES:
            assert isinstance(
                result, pd.DataFrame
            ), "The {} type can only be set with a DataFrame object".format(result_type)
            columns, data = resolve_data_frame(result)
            resolved["results"] = dict(data=data, columns=columns)
        elif result_type == ResultType.MULTIPLE_TIME_SERIES:
            assert isinstance(result, list) and all(
                [isinstance(res, pd.DataFrame) for res in result]
            ), "The {} type can only be set with a list of DataFrame objects".format(
                result_type
            )
            resolved["results"] = list()
            for res in result:
                columns, data = resolve_data_frame(res)
                resolved["results"].append(dict(columns=columns, data=data))
        elif result_type == ResultType.TEXT:
            assert isinstance(
                result, dict
            ), "The {} type can only be set with a dictionary".format(result_type)
            total = result.get("total")
            predict = result.get("predict")
            assert total is not None, "Field 'total' in text result is required."
            assert predict is not None, "Field 'predict' in text result is required."
            resolved["results"] = result
        else:
            raise ValueError("ResultType {} is not recognized".format(result_type))
        resolved["timestamp"] = (
            datetime.datetime.utcnow().astimezone(timezone.utc).isoformat(sep="T")
        )
        self.body = resolved
