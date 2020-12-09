"""
This module handles the prometheus metrics
"""

from prometheus_client import (
    Counter,
    Enum,
)


state = Enum(
    "ml_wrapper_state",
    "The state of the ML Tool",
    states=["alive", "error", "starting", "shutting down"],
)

error_counter = Counter("error_counter", "Counter of Errors occuring")

message_issue_counter = Counter(
    "message_issues",
    "Counts the incoming messages with an schema validation error or retrieval error",
)
