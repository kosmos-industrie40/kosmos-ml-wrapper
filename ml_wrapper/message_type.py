"""
This file provides the result type enumeration
"""
from enum import Enum


class MessageType(Enum):
    """
    Enum for the result Types of an analyse
    """

    SENSOR_UPDATE = "sensor_update"
    ANALYSES_Result = "analyse_result"

    @classmethod
    def value2member_map(cls):
        """
        Release the value2member_map function
        @return: dict
        """
        # pylint: disable=no-member
        return cls._value2member_map_
