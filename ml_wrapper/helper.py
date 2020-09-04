"""
This class provides helper functions
"""
import json
import jsonschema
from os.path import dirname, abspath, join
from typing import Union

from jsonschema import ValidationError

from ml_wrapper.exceptions import NonSchemaConformJsonPayload

FILE_DIR = dirname(abspath(__file__))

SCHEMA_DIR = abspath(join(FILE_DIR, "..", "docs", "MqttPayloads"))

with open(join(SCHEMA_DIR, "analyses-formal.json")) as file:
    ANALYSES_FORMAL = json.load(file)

with open(join(SCHEMA_DIR, "data-formal.json")) as file:
    DATA_FORMAL = json.load(file)


def _validate_formal_single(json_object: Union[str, dict], against=ANALYSES_FORMAL):
    assert isinstance(json_object, str) or isinstance(
        json_object, dict
    ), "I can only validate json objects as dictionaries or json strings"
    json_object = (
        json_object if isinstance(json_object, dict) else json.loads(json_object)
    )
    jsonschema.validate(json_object, against)


def validate_formal(json_object: Union[str, dict]) -> bool:
    """
    Validates a json dictionary or a json string against the formal json schemas
    @param json_object: str or dict
    @raises NonSchemaConformJsonPayload
    """
    validation_worked = False
    validation_error = []
    try:
        _validate_formal_single(json_object, ANALYSES_FORMAL)
        validation_worked = True
    except ValidationError as error:
        validation_error.append(error.message)
    try:
        _validate_formal_single(json_object, DATA_FORMAL)
        validation_worked = True
    except ValidationError as error:
        validation_error.append(error.message)
    if not validation_worked:
        raise NonSchemaConformJsonPayload("\n----\n".join(validation_error))
    return validation_worked
