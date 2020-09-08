"""
This class provides helper functions
"""
import json

from typing import Union

import jsonschema
from jsonschema import ValidationError

import pandas as pd

from .exceptions import NonSchemaConformJsonPayload
from .message_type import MessageType
from .result_type import ResultType

from .json_provider import TRIGGER_FORMAL, ANALYSES_FORMAL, DATA_FORMAL, SCHEMA_STORE


def _resolver(schema):
    return jsonschema.RefResolver.from_schema(schema, store=SCHEMA_STORE)


def validate_formal_single(
    json_object: Union[str, dict],
    against=ANALYSES_FORMAL,
):
    """
    Validates a json object against a json schema string with a Draft7Validator
    @param json_object: str, dict
    @param against: str - the schema
    """
    assert isinstance(
        json_object, (str, dict)
    ), "I can only validate json objects as dictionaries or json strings"
    json_object = (
        json_object if isinstance(json_object, dict) else json.loads(json_object)
    )
    resolver = _resolver(against)
    validator = jsonschema.Draft7Validator(schema=against, resolver=resolver)
    validator.validate(json_object)


def validate_formal(json_object: Union[str, dict]) -> Union[None, MessageType]:
    """
    Validates a json dictionary or a json string against the formal json schemas
    @param json_object: str or dict
    @raise NonSchemaConformJsonPayload
    """
    validation_type_result = None
    validation_error = []
    try:
        validate_formal_single(json_object, ANALYSES_FORMAL)
        validation_type_result = MessageType.ANALYSES_Result
    except ValidationError as error:
        validation_error.append(error.message)
    try:
        validate_formal_single(json_object, DATA_FORMAL)
        validation_type_result = MessageType.SENSOR_UPDATE
    except ValidationError as error:
        validation_error.append(error.message)
    if validation_type_result is None:
        raise NonSchemaConformJsonPayload("\n----\n".join(validation_error))
    return validation_type_result


def validate_trigger(json_object: Union[str, dict]) -> bool:
    """
    Validates a json dictionary or a json string against the formal trigger message
    @param json_object: str or dict
    @return: bool
    @raise NonSchemaConformJsonPayload
    """
    try:
        validate_formal_single(json_object, TRIGGER_FORMAL)
    except ValidationError as error:
        raise NonSchemaConformJsonPayload(error) from error
    return True


# pylint: disable=no-else-return
def find_result_type(result) -> ResultType:
    """
    This method checks a few conditions to find the ResultType of a message. If none is matching,
    None is returned.

    @param result: the result to be checked
    @return: ResultType
    """
    checks = [
        isinstance(result, pd.DataFrame),
        isinstance(result, list),
        isinstance(result, dict),
    ]
    if not any(checks) or sum(checks) != 1:
        return None
    if checks[0]:
        return ResultType.TIME_SERIES
    elif checks[1] and all([isinstance(res, pd.DataFrame) for res in result]):
        return ResultType.MULTIPLE_TIME_SERIES
    elif checks[2] and all([key in result.keys() for key in ["total", "predict"]]):
        return ResultType.TEXT
    else:
        return None
