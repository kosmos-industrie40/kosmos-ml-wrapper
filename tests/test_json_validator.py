"""
This file provides tests for the helper file
"""
import json
import unittest
from unittest import TestCase

from src.ml_wrapper.json_provider import (
    JSON_DATA_EXAMPLE_3,
    JSON_ANALYSE_TIME_SERIES,
    JSON_ML_ANALYSE_TEXT,
    JSON_ML_DATA_EXAMPLE,
)
from src.ml_wrapper.json_validator import (
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
        bad_analyses = json.loads(json.dumps(JSON_ANALYSE_TIME_SERIES))
        bad_analyses["body"]["timestamp"] = 12345
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, bad_analyses)
        del bad_analyses["body"]["timestamp"]
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, bad_analyses)

    def test_validate_trigger(self):
        analyses = json.loads(json.dumps(JSON_ML_ANALYSE_TEXT))
        data = json.loads(json.dumps(JSON_ML_DATA_EXAMPLE))
        analyses["body"]["payload"] = json.loads(json.dumps(JSON_ANALYSE_TIME_SERIES))
        # print(json.dumps(JSON_ANALYSE_TIME_SERIES, indent=4, sort_keys=True))
        data["body"]["payload"] = json.loads(json.dumps(JSON_DATA_EXAMPLE_3))
        # print(json.dumps(analyses, indent=4, sort_keys=True))
        validate_trigger(analyses)
        validate_trigger(data)
        analyses["body"]["payload"]["body"] = "corrupt"
        print(json.dumps(analyses, indent=4, sort_keys=True))
        self.assertRaises(NonSchemaConformJsonPayload, validate_formal, analyses)
        self.assertRaises(NonSchemaConformJsonPayload, validate_trigger, analyses)


if __name__ == "__main__":
    unittest.main()
