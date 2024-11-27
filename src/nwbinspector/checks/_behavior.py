"""Checks for types belonging to the pynwb.behavior module."""

from typing import Iterable, Optional

import numpy as np
from pynwb.behavior import CompassDirection, SpatialSeries

from .._registration import Importance, InspectorMessage, register_check


@register_check(importance=Importance.CRITICAL, neurodata_type=SpatialSeries)
def check_spatial_series_dims(spatial_series: SpatialSeries) -> Optional[InspectorMessage]:
    """
    Check if a SpatialSeries has the correct dimensions.

    Best Practice: :ref:`best_practice_spatial_series_dimensionality`
    """
    if len(spatial_series.data.shape) > 1 and spatial_series.data.shape[1] > 3:
        return InspectorMessage(
            message="SpatialSeries should have 1 column (x), 2 columns (x, y), or 3 columns (x, y, z)."
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=CompassDirection)
def check_compass_direction_unit(compass_direction: CompassDirection) -> Optional[Iterable[InspectorMessage]]:
    """
    Check that SpatialSeries objects within CompassDirection objects have units 'degrees' or 'radians'.

    Best Practice: :ref:`best_practice_spatial_series_units`
    """
    for spatial_series in compass_direction.spatial_series.values():
        if spatial_series.unit not in ("degrees", "radians"):
            yield InspectorMessage(
                message=f"SpatialSeries objects inside a CompassDirection object should be angular and should have a "
                f"unit of 'degrees' or 'radians', but '{spatial_series.name}' has units '{spatial_series.unit}'."
            )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=SpatialSeries)
def check_spatial_series_radians_magnitude(
    spatial_series: SpatialSeries, nelems: int = 200
) -> Optional[InspectorMessage]:
    """
    Check that SpatialSeries with units radians have data values between -2*pi and 2*pi.

    Best Practice: :ref:`best_practice_spatial_series_values`
    """
    if spatial_series.unit in ("radian", "radians"):
        data = spatial_series.data[:nelems]
        if np.any(data > (2 * np.pi)) or np.any(data < (-2 * np.pi)):
            return InspectorMessage(
                message="SpatialSeries with units of radians must have values between -2pi and 2pi."
            )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=SpatialSeries)
def check_spatial_series_degrees_magnitude(
    spatial_series: SpatialSeries, nelems: int = 200
) -> Optional[InspectorMessage]:
    """
    Check that SpatialSeries with units of degrees have data values between -360 and 360.

    Best Practice: :ref:`best_practice_spatial_series_values`
    """
    if spatial_series.unit in ("degree", "degrees"):
        data = spatial_series.data[:nelems]
        if np.any(data > 360) or np.any(data < -360):
            return InspectorMessage(
                message="SpatialSeries with units of degrees must have values between -360 and 360."
            )

    return None
