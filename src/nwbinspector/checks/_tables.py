"""Check functions that can apply to any descendant of DynamicTable."""

from numbers import Real
from typing import Iterable, Optional

import numpy as np
from hdmf.common import DynamicTable, DynamicTableRegion, VectorIndex
from pynwb.file import TimeIntervals, Units

from .._registration import Importance, InspectorMessage, register_check
from ..utils import (
    cache_data_selection,
    format_byte_size,
    get_data_shape,
    is_ascending_series,
    is_dict_in_string,
    is_string_json_loadable,
)

NELEMS = 200


@register_check(importance=Importance.CRITICAL, neurodata_type=DynamicTableRegion)
def check_dynamic_table_region_data_validity(
    dynamic_table_region: DynamicTableRegion, nelems: Optional[int] = NELEMS
) -> Optional[InspectorMessage]:
    """Check if a DynamicTableRegion is valid."""
    if np.any(np.asarray(dynamic_table_region.data[:nelems]) > len(dynamic_table_region.table)):
        return InspectorMessage(
            message=(
                f"Some elements of {dynamic_table_region.name} are out of range because they are greater than the "
                "length of the target table. Note that data should contain indices, not ids."
            )
        )
    if np.any(np.asarray(dynamic_table_region.data[:nelems]) < 0):
        return InspectorMessage(
            message=f"Some elements of {dynamic_table_region.name} are out of range because they are less than 0."
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=DynamicTable)
def check_empty_table(table: DynamicTable) -> Optional[InspectorMessage]:
    """Check if a DynamicTable is empty."""
    if len(table.id) == 0:
        return InspectorMessage(message="This table has no data added to it.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=TimeIntervals)
def check_time_interval_time_columns(
    time_intervals: TimeIntervals, nelems: Optional[int] = NELEMS
) -> Optional[InspectorMessage]:
    """
    Check that time columns are in ascending order.

    Parameters
    ----------
    time_intervals: TimeIntervals
    nelems: int, optional
        Only check the first {nelems} elements. This is useful in case there columns are
        very long so you don't need to load the entire array into memory. Use None to
        load the entire arrays.
    """
    unsorted_cols = []
    for column in time_intervals.columns:
        if column.name == "start_time":
            if not is_ascending_series(column.data, nelems):
                unsorted_cols.append(column.name)
    if unsorted_cols:
        return InspectorMessage(
            message=(
                f"{unsorted_cols} are time columns but the values are not in ascending order. "
                "All times should be in seconds with respect to the session start time."
            )
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=TimeIntervals)
def check_time_intervals_stop_after_start(
    time_intervals: TimeIntervals, nelems: Optional[int] = NELEMS
) -> Optional[InspectorMessage]:
    """
    Check that all stop times on a TimeInterval object occur after their corresponding start times.

    Best Practice: :ref:`best_practice_time_interval_time_columns`

    Parameters
    ----------
    time_intervals: TimeIntervals
    nelems: int, optional
        Only check the first {nelems} elements. This is useful in case there columns are
        very long so you don't need to load the entire array into memory. Use None to
        load the entire arrays.
    """
    if np.any(
        np.asarray(cache_data_selection(data=time_intervals["stop_time"].data, selection=slice(nelems)))
        - np.asarray(cache_data_selection(data=time_intervals["start_time"].data, selection=slice(nelems)))
        < 0
    ):
        return InspectorMessage(
            message=(
                "stop_times should be greater than start_times. Make sure the stop times are with respect to the "
                "session start time."
            )
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=DynamicTable)
def check_column_binary_capability(
    table: DynamicTable, nelems: Optional[int] = NELEMS
) -> Optional[Iterable[InspectorMessage]]:
    """
    Check each column of a table to see if the data could be set as a boolean dtype.

    Parameters
    ----------
    table: DynamicTable
    nelems: int, optional
        Only check the first {nelems} elements. This is useful in case there columns are
        very long so you don't need to load the entire array into memory. Use None to
        load the entire arrays.
    """
    pre_defined_column_names = [column["name"] for column in getattr(table, "__columns__", list())]
    for column in table.columns:
        if column.name in pre_defined_column_names:
            continue  # The column name and data type cannot be changed by the user
        if hasattr(column, "data") and not isinstance(column, VectorIndex):
            if np.asarray(column.data[0]).itemsize == 1:
                continue  # already boolean, int8, or uint8
            try:
                unique_values = np.unique(cache_data_selection(data=column.data, selection=slice(nelems)))
            except TypeError:  # some contained objects are unhashable or have no comparison defined
                continue
            if unique_values.size != 2:
                continue
            parsed_unique_values = np.array(unique_values)
            if isinstance(parsed_unique_values[0], Real):  # upcast to float for comparison
                parsed_unique_values = parsed_unique_values.astype(float)
            elif str(parsed_unique_values.dtype)[:2] == "<U":  # parse strings as all lower-case
                for j in range(2):
                    parsed_unique_values[j] = parsed_unique_values[j].lower()
            pairs_to_check = [
                [1.0, 0.0],
                ["yes", "no"],
                ["y", "n"],
                ["true", "false"],
                ["t", "f"],
                ["hit", "miss"],
            ]
            if any([set(parsed_unique_values) == set(pair) for pair in pairs_to_check]):  # type: ignore
                saved_bytes = (unique_values.dtype.itemsize - 1) * np.prod(
                    get_data_shape(data=column.data, strict_no_data_load=True)
                )
                if unique_values.dtype == "float":
                    print_dtype = "floats"
                elif unique_values.dtype == "int":
                    print_dtype = "integers"
                elif str(unique_values.dtype)[:2] == "<U":
                    print_dtype = "strings"
                else:
                    print_dtype = f"{unique_values.dtype}"
                yield InspectorMessage(
                    message=(
                        f"Column '{column.name}' uses '{print_dtype}' but has binary values {unique_values}. Consider "
                        "making it boolean instead and renaming the column to start with 'is_'; doing so will "
                        f"save {format_byte_size(byte_size=saved_bytes)}."
                    )
                )
    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=DynamicTable)
def check_single_row(
    table: DynamicTable,
    exclude_types: Optional[tuple] = None,
    exclude_names: Optional[tuple[str]] = None,
) -> Optional[InspectorMessage]:
    """
    Check if DynamicTable has only a single row; may be better represented by another data type.

    Skips the Units table since it is OK to have only a single spiking unit.
    Skips the Electrode table since it is OK to have only a single electrode.
    """
    exclude_types = exclude_types or (Units,)
    exclude_names = exclude_names or ("electrodes",)

    if any((isinstance(table, exclude_type) for exclude_type in exclude_types)):
        return None
    if any((table.name == exclude_name for exclude_name in exclude_names)):
        return None
    if len(table.id) == 1:
        return InspectorMessage(
            message="This table has only a single row; it may be better represented by another data type."
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=DynamicTable)
def check_table_values_for_dict(
    table: DynamicTable, nelems: Optional[int] = NELEMS
) -> Optional[Iterable[InspectorMessage]]:
    """Check if any values in a row or column of a table contain a string casting of a Python dictionary."""
    for column in table.columns:
        if not hasattr(column, "data") or isinstance(column, VectorIndex) or not isinstance(column.data[0], str):
            continue
        for string in cache_data_selection(data=column.data, selection=slice(nelems)):
            if is_dict_in_string(string=string):
                message = (
                    f"The column '{column.name}' contains a string value that contains a dictionary! Please "
                    "unpack dictionaries as additional rows or columns of the table."
                )
                if is_string_json_loadable(string=string):
                    message += " This string is also JSON loadable, so call `json.loads(...)` on the string to unpack."
                yield InspectorMessage(message=message)

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=DynamicTable)
def check_col_not_nan(table: DynamicTable, nelems: Optional[int] = NELEMS) -> Optional[Iterable[InspectorMessage]]:
    """Check if all the values in a single column of a table are NaN."""
    for column in table.columns:
        if (
            not hasattr(column, "data")
            or isinstance(column, VectorIndex)
            or not np.issubdtype(np.array(column[0]).dtype, np.floating)
        ):
            continue
        if nelems is not None and not all(np.isnan(column[:nelems]).flatten()):
            continue

        slice_by = np.ceil(len(column.data) / nelems).astype(int) if nelems else None
        message = f"Column '{column.name}' might have all NaN values. Consider removing it from the table."
        message = message.replace("might have", "has") if nelems is None or slice_by == 1 else message
        if all(np.isnan(column[slice(0, None, slice_by)]).flatten()):
            yield InspectorMessage(message=message)

    return None


@register_check(importance=Importance.CRITICAL, neurodata_type=DynamicTable)
def check_ids_unique(table: DynamicTable, nelems: Optional[int] = NELEMS) -> Optional[InspectorMessage]:
    """
    Ensure that the values of the id attribute of a DynamicTable are unique.

    Best Practice: :ref:`best_practice_unique_dynamic_table_ids`

    Parameters
    ----------
    table: DynamicTable
    nelems: int, optional
        Only inspect the first {nelems} elements

    Returns
    -------

    """
    data = table.id[:nelems]
    if len(set(data)) != len(data):
        return InspectorMessage(message="This table has ids that are not unique.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=DynamicTable)
def check_table_time_columns_are_not_negative(table: DynamicTable) -> Optional[Iterable[InspectorMessage]]:
    """
    Check that time columns are not negative.

    Best Practice: :ref:`best_practice_global_time_reference`

    Parameters
    ----------
    table: DynamicTable
    """
    for column_name in table.colnames:
        if column_name.endswith("_time"):
            first_timestamp = table[column_name][0]
            if first_timestamp < 0:
                yield InspectorMessage(
                    message=f"Timestamps in column {column_name} should not be negative."
                    " It is recommended to align the `session_start_time` or `timestamps_reference_time` to be the earliest time value that occurs in the data, and shift all other signals accordingly."
                )

    return None
