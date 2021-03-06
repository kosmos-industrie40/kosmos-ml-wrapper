"""
This file holds the exceptions used
"""


class WrongMessageType(Exception):
    """
    Represents the exception of a wrong message type
    """


class NotInitialized(Exception):
    """
    Represents the error of an uninitialized object
    """


class NotYetRetrieved(Exception):
    """
    Represents the error of an Information object where the data is not retrieved yet
    """


class InvalidType(Exception):
    """
    Represents the error of an Result or message type that is not valid
    """


class EmptyResult(Exception):
    """
    Represents the error case that a result in an analysis message is empty
    """


class InvalidTopic(Exception):
    """
    Represents the error case that a topic is invalid
    """


class NonSchemaConformJsonPayload(Exception):
    """
    This exception descirbes the error of a json object, that does not conform to the defined
    json schemas allowed.
    """


class ConfigNotValid(Exception):
    """
    This exception describes the error of a wrongly configured config file.
    """
