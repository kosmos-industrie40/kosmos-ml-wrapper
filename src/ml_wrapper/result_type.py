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

    @classmethod
    def value2member_map(cls):
        """
        Release the value2member_map function
        @return: dict
        """
        # pylint: disable=no-member
        return cls._value2member_map_
