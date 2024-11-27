"""Internally used tools specifically for rendering more human-readable output from collected check results."""

from enum import Enum
from typing import Optional

from natsort import natsorted

from ._registration import InspectorMessage


def _sort_unique_values(unique_values: list, reverse: bool = False) -> list:
    """Technically, the 'set' method applies basic sorting to the unique contents, but natsort is more general."""
    if any(unique_values) and isinstance(unique_values[0], Enum):
        return natsorted(unique_values, key=lambda x: -x.value, reverse=reverse)
    else:
        return natsorted(unique_values, reverse=reverse)


def organize_messages(
    messages: list[Optional[InspectorMessage]], levels: list[str], reverse: Optional[list[bool]] = None
) -> dict:
    """
    General function for organizing list of InspectorMessages.

    Returns a nested dictionary organized according to the order of the 'levels' argument.

    Parameters
    ----------
    messages : list of InspectorMessages
    levels : list of strings
        Each string in this list must correspond onto an attribute of the InspectorMessage class, excluding the
        'message' text and 'object_name' (this will be coupled to the 'object_type').
    reverse : list of bool, optional
        If provided, this should be a list of booleans that correspond to the 'levels' argument.
        If True, the values will be sorted in reverse order.
    """
    assert all([x not in levels for x in ["message", "object_name", "severity"]]), (
        "You must specify levels to organize by that correspond to attributes of the InspectorMessage class, excluding "
        "the text message, object_name, and severity."
    )
    if reverse is None:
        reverse = [False] * len(levels)
    unique_values = list(set(getattr(message, levels[0]) for message in messages))
    sorted_values = _sort_unique_values(unique_values, reverse=reverse[0])
    if len(levels) > 1:
        return {
            value: organize_messages(
                messages=[message for message in messages if getattr(message, levels[0]) == value],
                levels=levels[1:],
                reverse=reverse[1:],
            )
            for value in sorted_values
        }
    else:
        return {
            value: sorted(
                [message for message in messages if getattr(message, levels[0]) == value],
                key=lambda x: -x.severity.value,
            )
            for value in sorted_values
        }
