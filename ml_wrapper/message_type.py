"""
This file provides the result type enumeration
"""
from enum import Enum


class MessageType(Enum):
    """
    Enum for the result Types of an analyse
    """

    DATA = "data"
    ANALYSES = "analyses"
