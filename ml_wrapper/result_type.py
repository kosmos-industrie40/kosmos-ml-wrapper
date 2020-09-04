"""
This file provides the result type enumeration
"""
from enum import Enum


class ResultType(Enum):
    """
    Enum for the result Types of an analyse
    """

    TEXT = "text"
    TIME_SERIES = "time_series"
    MULTIPLE_TIME_SERIES = "multiple_time_series"
