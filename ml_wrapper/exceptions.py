"""
This file holds the exceptions used
"""


class NonSchemaConformJsonPayload(Exception):
    """
    This exception descirbes the error of a json object, that does not conform to the defined
    json schemas allowed.
    """
