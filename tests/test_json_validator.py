"""
This file provides tests for the helper file
"""
import unittest
from unittest import TestCase

from ml_wrapper.json_provider import (
    JSON_DATA_EXAMPLE_3,
    JSON_ANALYSE_TIME_SERIES,
    JSON_ML_ANALYSE_TEXT,
    JSON_ML_DATA_EXAMPLE,
)
from ml_wrapper.json_validator import (
    NonSchemaConformJsonPayload,
    validate_formal,
    validate_trigger,
)


class Test(TestCase):
    """
    This test case provides tests for the validation of a json object according to the docs
    """

    def test_validate_formal(self):
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, '{"test": 1}')
        self.assertTrue(validate_formal(JSON_DATA_EXAMPLE_3))
        self.assertTrue(validate_formal(JSON_ANALYSE_TIME_SERIES))
        bad_analyses = dict(JSON_ANALYSE_TIME_SERIES)
        bad_analyses["timestamp"] = 12345
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, bad_analyses)
        del bad_analyses["timestamp"]
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, bad_analyses)

    def test_validate_trigger(self):
        analyses = dict(JSON_ML_ANALYSE_TEXT)
        data = dict(JSON_ML_DATA_EXAMPLE)
        analyses["payload"] = JSON_ANALYSE_TIME_SERIES
        data["payload"] = JSON_DATA_EXAMPLE_3
        validate_trigger(analyses)
        validate_trigger(data)
        analyses["payload"] = "corrupt"
        self.assertRaises(NonSchemaConformJsonPayload, validate_trigger, analyses)


if __name__ == "__main__":
    unittest.main()
