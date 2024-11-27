"""Checks specific to the Images neurodata type."""

from typing import Optional

from pynwb.base import Images
from pynwb.image import IndexSeries

from .._registration import Importance, InspectorMessage, register_check


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=Images)
def check_order_of_images_unique(images: Images) -> Optional[InspectorMessage]:
    """Check that all the values in the order_of_images field of an Images object are unique."""
    if images.order_of_images is None:
        return None
    if not len(set(images.order_of_images)) == len(images.order_of_images):
        return InspectorMessage(message="order_of_images should have unique values.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=Images)
def check_order_of_images_len(images: Images) -> Optional[InspectorMessage]:
    """Check that all the values in the order_of_images field of an Images object are unique."""
    if images.order_of_images is None:
        return None
    if not len(images.order_of_images) == len(images.images):
        return InspectorMessage(
            message=f"Length of order_of_images ({len(images.order_of_images)}) does not match the number of "
            f"images ({len(images.images)})."
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=IndexSeries)
def check_index_series_points_to_image(index_series: IndexSeries) -> Optional[InspectorMessage]:
    if index_series.indexed_timeseries is not None:
        return InspectorMessage(
            message="Pointing an IndexSeries to a TimeSeries will be deprecated. Please point to an Images "
            "container instead."
        )

    return None
