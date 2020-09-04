"""
This file provides tests for the helper file
"""
import json
from os.path import dirname, abspath, join
from unittest import TestCase

from ml_wrapper import NonSchemaConformJsonPayload, validate_formal


FILE_DIR = dirname(abspath(__file__))

SCHEMA_DIR = abspath(join(FILE_DIR, "..", "docs", "MqttPayloads"))

with open(join(SCHEMA_DIR, "analyses-example-time_series.json")) as file:
    ANALYSES_EXAMPLE_TIME_SERIES = json.load(file)

with open(join(SCHEMA_DIR, "data-example-3.json")) as file:
    DATA_EXAMPLE = json.load(file)


class Test(TestCase):
    """
    This test case provides tests for the validation of a json object according to the docs
    """

    def test_validate_formal(self):
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, '{"test": 1}')
        self.assertTrue(validate_formal(DATA_EXAMPLE))
        self.assertTrue(validate_formal(ANALYSES_EXAMPLE_TIME_SERIES))
        bad_analyses = dict(ANALYSES_EXAMPLE_TIME_SERIES)
        bad_analyses["timestamp"] = 12345
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, bad_analyses)
        del bad_analyses["timestamp"]
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, bad_analyses)
