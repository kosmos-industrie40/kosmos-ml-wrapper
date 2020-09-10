"""
Init file that organizes the base level imports
"""
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution, DistributionNotFound
from .json_provider import *
from .result_type import *
from .message_type import *
from .messaging import *
from .ml_wrapper import MLWrapper

try:
    # Change here if project is renamed and does not equal the package name
    DIST_NAME = __name__
    __version__ = get_distribution(DIST_NAME).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
