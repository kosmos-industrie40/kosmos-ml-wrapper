"""
This module provides the log_level
"""

import logging
from os.path import dirname
from iniparser import Config

# pylint: disable=invalid-name
config = Config().scan(dirname(__file__), recursive=False).read()

# Pylint falsly doesn't recognize the get function of the config object
# pylint: disable=no-member
LOG_LEVEL = logging.getLevelName(
    config.get("logging", "log_level", default="INFO").upper()
)

logging.basicConfig(level=LOG_LEVEL)
