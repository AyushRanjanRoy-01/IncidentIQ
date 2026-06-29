"""Helper utility functions."""

import uuid
from datetime import datetime
from typing import Any


def generate_id() -> str:
    """Generate unique ID.

    Returns:
        Unique ID string
    """
    return str(uuid.uuid4())


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO 8601 timestamp.

    Args:
        ts: Timestamp string

    Returns:
        Datetime object
    """
    # TODO: Implement timestamp parsing
    pass


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    # TODO: Format duration
    pass


def merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """
    # TODO: Implement deep merge
    pass
