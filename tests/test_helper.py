"""
This file provides tests for the helper file
"""
import json
import unittest
from os.path import dirname, abspath, join
from unittest import TestCase

from ml_wrapper.helper import topic_splitter


class Test(TestCase):
    """
    This test case provides tests for the helper class
    """

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
