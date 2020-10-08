"""
This file holds the exceptions used
"""


class WrongMessageType(Exception):
    """
    Represents the exception of a wrong message type
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class NotInitialized(Exception):
    """
    Represents the error of an uninitialized object
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class NotYetRetrieved(Exception):
    """
    Represents the error of an Information object where the data is not retrieved yet
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class InvalidType(Exception):
    """
    Represents the error of an Result or message type that is not valid
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class EmptyResult(Exception):
    """
    Represents the error case that a result in an analysis message is empty
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class InvalidTopic(Exception):
    """
    Represents the error case that a topic is invalid
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class NonSchemaConformJsonPayload(Exception):
    """
    This exception descirbes the error of a json object, that does not conform to the defined
    json schemas allowed.
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()


class ConfigNotValid(Exception):
    """
    This exception describes the error of a wrongly configured config file.
    """
    def __init__(self, message = ""):
        self.message = message
        super().__init__()
