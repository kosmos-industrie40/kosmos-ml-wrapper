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

    def __eq__(self, other):
        if not hasattr(other, "value"):
            print("Other is different instance")
            return False
        return self.value == other.value

    @classmethod
    def value2member_map(cls):
        """
        Release the value2member_map function
        @return: dict
        """
        # pylint falsly doesn't detect the private method
        # _value2member_map_
        # pylint: disable=no-member
        return cls._value2member_map_
