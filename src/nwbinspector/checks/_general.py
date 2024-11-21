"""Check functions that examine any general neurodata_type with the available attributes."""

from typing import Optional

from .._registration import Importance, InspectorMessage, register_check

COMMON_DESCRIPTION_PLACEHOLDERS = ["no description", "no desc", "none", "placeholder"]


@register_check(importance=Importance.CRITICAL, neurodata_type=None)
def check_name_slashes(neurodata_object: object) -> Optional[InspectorMessage]:
    """Check if there  has been added for the session."""
    if hasattr(neurodata_object, "name") and any((x in neurodata_object.name for x in ["/", "\\"])):
        return InspectorMessage(message="Object name contains slashes.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=None)
def check_description(neurodata_object: object) -> Optional[InspectorMessage]:
    """
    Check if the description is a not missing or a placeholder.

    Best Practice: :ref:`best_practice_placeholders`
    """
    if not hasattr(neurodata_object, "description") or type(neurodata_object.description) is not str:
        return None
    if neurodata_object.description is None or neurodata_object.description.strip(" ") == "":
        return InspectorMessage(message="Description is missing.")
    if neurodata_object.description.lower().strip(".") in COMMON_DESCRIPTION_PLACEHOLDERS:
        return InspectorMessage(message=f"Description ('{neurodata_object.description}') is a placeholder.")

    return None
