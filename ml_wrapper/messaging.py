"""
This provides a Messaging object which logic is used to pass on information between the stages of
the ML Wrapper Tool
"""
import inspect
import json
from json.decoder import JSONDecodeError

from paho.mqtt.client import MQTTMessage

from ml_wrapper import validate_formal, MessageType, ResultType
from ml_wrapper.convert_data import retrieve_sensor_update_data, retrieve_dataframe
from .exceptions import (
    NotInitialized,
    NonSchemaConformJsonPayload,
    NotYetRetrieved,
    InvalidType,
    NotYetImplemented,
    EmptyResult,
)


class IncomingMessage:
    """
    This class represents a Messaging object to pass on information between the stages of the
    ML Wrapper
    """

    def __init__(self):
        self._message_type = None
        self._message_data_type = None
        self._topic = None
        self._payload = None
        self._mqtt_message = None
        self._retrieved_data = None
        self._columns = None
        self._data = None
        self._metadata = None
        self._timestamp = None
        self.custom_information_field = None

    @property
    def retrieved_data(self):
        return self._retrieved_data

    @property
    def columns(self):
        return self._columns

    @property
    def data(self):
        return self._data

    @property
    def metadata(self):
        return self._metadata

    @property
    def timestamp(self):
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
        msg = self.payload
        timestamp = msg.get("timestamp")
        if self._message_type is MessageType.ANALYSES:
            try:
                msg_type = ResultType.value2member_map()[msg.get("type")]
            except KeyError as e:
                raise InvalidType(e) from e
            self.message_data_type = msg_type
            if msg_type == ResultType.TIME_SERIES:
                results = msg.get("results")
                if results is None:
                    raise EmptyResult("The result of a message cannot be empty")
                retrieved_data, columns, data = retrieve_dataframe(results)
            elif msg_type == ResultType.TEXT:
                results = msg.get("results")
                if results is None:
                    raise EmptyResult("The result of a message cannot be empty")
                retrieved_data = results
            elif msg_type == ResultType.MULTIPLE_TIME_SERIES:
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
                    "This message type {} has not been implemented".format(msg_type)
                )
        elif self._message_type is MessageType.DATA:
            retrieved_data, columns, data, metadata = retrieve_sensor_update_data(msg)
        else:
            raise NotImplemented(
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
    def message_data_type(self):
        """ Returns the protected property for message_data_type """
        return self._message_data_type

    @message_data_type.setter
    def message_data_type(self, new_value: ResultType):
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

    @message_data_type.deleter
    def message_data_type(self):
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

    @mqtt_message.deleter
    def mqtt_message(self):
        """ Deletes the protected property for mqtt_message """
        del self._mqtt_message

    def _initialize_with_message(self):
        assert (
            self._mqtt_message is not None
        ), "MQTT Message needs to be set prior to this method"
        self.payload = self.mqtt_message.payload
        self.topic = self.mqtt_message.topic

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
        try:
            payload = json.loads(new_value)
        except JSONDecodeError as e:
            raise e from e
        message_type = False
        try:
            message_type = validate_formal(payload)
        except NonSchemaConformJsonPayload as e:
            raise e from e
        self._message_type = message_type
        self._payload = payload

    @payload.deleter
    def payload(self):
        """ Deletes the protected property for payload """
        del self._payload

    @property
    def topic(self):
        """ Returns the protected property for topic """
        return self._topic

    @topic.setter
    def topic(self, new_value: str):
        """
        Sets the protected property for topic
        :param new_value:
        """
        self._topic = new_value

    @topic.deleter
    def topic(self):
        """ Deletes the protected property for topic """
        del self._topic


if __name__ == "__main__":
    inf = IncomingMessage()
    print(inf.topic)
