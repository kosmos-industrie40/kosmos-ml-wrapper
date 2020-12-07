"""
This module provides the different status states
"""
from enum import Enum


class ToolState(Enum):
    """
    Represents the state of the ML Tool
    """

    ALIVE = "alive"
    ERROR = "error"
    STARTING = "starting"
    SHUTTING_DOWN = "shutting down"
