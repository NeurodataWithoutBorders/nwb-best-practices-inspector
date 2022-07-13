"""Check functions that can apply to any descendant of TimeSeries."""
from typing import Optional

import numpy as np
from pynwb import TimeSeries

from ..register_checks import register_check, Importance, Severity, InspectorMessage
from ..utils import check_regular_series, is_ascending_series, get_uniform_indexes


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=TimeSeries)
def check_regular_timestamps(
    time_series: TimeSeries, time_tolerance_decimals: int = 9, gb_severity_threshold: float = 1.0
):
    """If the TimeSeries uses timestamps, check if they are regular (i.e., they have a constant rate)."""
    if (
        time_series.timestamps is not None
        and len(time_series.timestamps) > 2
        and check_regular_series(series=time_series.timestamps, tolerance_decimals=time_tolerance_decimals)
    ):
        timestamps = np.array(time_series.timestamps)
        if timestamps.size * timestamps.dtype.itemsize > gb_severity_threshold * 1e9:
            severity = Severity.HIGH
        else:
            severity = Severity.LOW
        return InspectorMessage(
            severity=severity,
            message=(
                "TimeSeries appears to have a constant sampling rate. "
                f"Consider specifying starting_time={time_series.timestamps[0]} "
                f"and rate={time_series.timestamps[1] - time_series.timestamps[0]} instead of timestamps."
            ),
        )


@register_check(importance=Importance.CRITICAL, neurodata_type=TimeSeries)
def check_data_orientation(time_series: TimeSeries):
    """If the TimeSeries has data, check if the longest axis (almost always time) is also the zero-axis."""
    if time_series.data is not None and any(np.array(time_series.data.shape[1:]) > time_series.data.shape[0]):
        return InspectorMessage(
            message=(
                "Data may be in the wrong orientation. "
                "Time should be in the first dimension, and is usually the longest dimension. "
                "Here, another dimension is longer."
            ),
        )


@register_check(importance=Importance.CRITICAL, neurodata_type=TimeSeries)
def check_timestamps_match_first_dimension(time_series: TimeSeries):
    """
    If the TimeSeries has timestamps, check if their length is the same as the zero-axis of data.

    Best Practice: :ref:`best_practice_data_orientation`
    """
    if (
        time_series.data is not None
        and time_series.timestamps is not None
        and np.array(time_series.data).shape[:1] != np.array(time_series.timestamps).shape
    ):
        return InspectorMessage(
            message="The length of the first dimension of data does not match the length of timestamps.",
        )


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=TimeSeries)
def check_timestamps_ascending(time_series: TimeSeries, nelems=200):
    """Check that the values in the timestamps array are strictly increasing."""
    if time_series.timestamps is not None and not is_ascending_series(time_series.timestamps, nelems=nelems):
        return InspectorMessage(f"{time_series.name} timestamps are not ascending.")


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=TimeSeries)
def check_missing_unit(time_series: TimeSeries):
    """
    Check if the TimeSeries.unit field is empty.

    Best Practice: :ref:`best_practice_unit_of_measurement`
    """
    if not time_series.unit:
        return InspectorMessage(
            message="Missing text for attribute 'unit'. Please specify the scientific unit of the 'data'."
        )


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=TimeSeries)
def check_resolution(time_series: TimeSeries):
    """Check the resolution value of a TimeSeries for proper format (-1.0 or NaN for unknown)."""
    if time_series.resolution is None or time_series.resolution == -1.0:
        return
    if time_series.resolution <= 0:
        return InspectorMessage(
            message=f"'resolution' should use -1.0 or NaN for unknown instead of {time_series.resolution}."
        )


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=TimeSeries)
def check_for_shared_timestamps(time_series: TimeSeries, nelems: Optional[int] = 200):
    """
    Check if any of the timestamps of other TimeSeries in the NWBFile are equivalent to this one.

    Technically, the check as implemented now does not leverage summetry across independent calls over the objects.
    """
    if time_series.timestamps is None:
        return

    nwbfile = time_series.get_ancestor("NWBFile")
    for nwbfile_object in nwbfile.objects.values():
        if nwbfile_object == time_series or not issubclass(type(nwbfile_object), TimeSeries):
            continue
        if nwbfile_object.timestamps is None or time_series.timestamps.shape != nwbfile_object.timestamps.shape:
            continue
        if np.array_equal(time_series.timestamps[:nelems], nwbfile_object.timestamps[:nelems]):
            continue

        subsample_indexes = get_uniform_indexes(length=time_series.timestamps.shape[0], nelems=nelems)
        if time_series.timestamps[subsample_indexes] == nwbfile_object.timestamps[subsample_indexes]:
            return InspectorMessage(
                message=(
                    "The timestamps of this TimeSeries appear to be equivalent to the timestamps of "
                    f"{nwbfile_object.name}! You can save file space by linking one to the other."
                )
            )
