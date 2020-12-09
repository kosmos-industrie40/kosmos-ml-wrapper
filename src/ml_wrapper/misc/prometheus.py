"""
This module handles the prometheus metrics
"""

from prometheus_client import (
    make_asgi_app,
    make_wsgi_app,
    Counter,
    Gauge,
    Histogram,
    Enum,
    Info,
)

info = Info("settings", "Settings provided to the ML Wrapper")

state = Enum(
    "ml_wrapper_state",
    "The state of the ML Tool",
    states=["alive", "error", "starting", "shutting down"],
)
# state.state("starting")

error_counter = Counter("error_counter", "Counter of Errors occuring")

message_issue_counter = Counter(
    "message_issues",
    "Counts the incoming messages with an schema validation error or retrieval error",
)
