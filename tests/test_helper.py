"""
This file provides tests for the helper file
"""
import json
import unittest
from os.path import dirname, abspath, join
from unittest import TestCase

from ml_wrapper.helper import (
    NonSchemaConformJsonPayload,
    validate_formal,
    validate_trigger,
    topic_splitter,
)

FILE_DIR = dirname(abspath(__file__))

SCHEMA_DIR = abspath(join(FILE_DIR, "..", "docs", "MqttPayloads"))

with open(join(SCHEMA_DIR, "analyses-example-time_series.json")) as file:
    ANALYSES_EXAMPLE_TIME_SERIES = json.load(file)

with open(join(SCHEMA_DIR, "data-example-3.json")) as file:
    DATA_EXAMPLE = json.load(file)

with open(join(SCHEMA_DIR, "ml-analyses-example.json")) as file:
    ML_ANALYSES = json.load(file)

with open(join(SCHEMA_DIR, "ml-update-example.json")) as file:
    ML_DATA = json.load(file)


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

    def test_validate_trigger(self):
        analyses = dict(ML_ANALYSES)
        data = dict(ML_DATA)
        analyses["payload"] = ANALYSES_EXAMPLE_TIME_SERIES
        data["payload"] = DATA_EXAMPLE
        validate_trigger(analyses)
        validate_trigger(data)
        analyses["payload"] = "corrupt"
        self.assertRaises(NonSchemaConformJsonPayload, validate_trigger, analyses)

    def test_topic_splitter(self):
        self.assertRaises(AssertionError, topic_splitter, dict(test=True))
        topics = ["a/b/c", "a/bc", "abc/t"]
        self.assertEqual(topics, topic_splitter(",".join(topics)))
        self.assertEqual(topics, topic_splitter(", ".join(topics)))
        self.assertEqual(["a", "b"], topic_splitter("a,b"))
        self.assertEqual(["a", "b"], topic_splitter("a|b", sep="|"))
        self.assertEqual(["a/b/c"], topic_splitter("a/b/c", sep="|"))


if __name__ == "__main__":
    unittest.main()
