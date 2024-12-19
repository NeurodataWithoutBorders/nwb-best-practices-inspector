import json
import platform
from unittest import TestCase

import numpy as np
from hdmf.common import DynamicTable, DynamicTableRegion
from numpy.lib import NumpyVersion
from pynwb.file import Device, ElectrodeGroup, ElectrodeTable, TimeIntervals, Units

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import (
    check_col_not_nan,
    check_column_binary_capability,
    check_dynamic_table_region_data_validity,
    check_empty_table,
    check_ids_unique,
    check_single_row,
    check_table_time_columns_are_not_negative,
    check_table_values_for_dict,
    check_time_interval_time_columns,
    check_time_intervals_stop_after_start,
)


class TestCheckDynamicTableRegion(TestCase):
    def setUp(self):
        self.table = DynamicTable(name="test_table", description="")
        self.table.add_column(name="test_column", description="")
        for _ in range(10):
            self.table.add_row(test_column=1)

    def test_check_dynamic_table_region_data_validity_lt_zero(self):
        dynamic_table_region = DynamicTableRegion(name="dyn_tab", description="desc", data=[-1, 0], table=self.table)

        assert check_dynamic_table_region_data_validity(dynamic_table_region) == InspectorMessage(
            message="Some elements of dyn_tab are out of range because they are less than 0.",
            importance=Importance.CRITICAL,
            check_function_name="check_dynamic_table_region_data_validity",
            object_type="DynamicTableRegion",
            object_name="dyn_tab",
            location="/",
        )

    def test_check_dynamic_table_region_data_validity_gt_len(self):
        dynamic_table_region = DynamicTableRegion(name="dyn_tab", description="desc", data=[0, 20], table=self.table)

        assert check_dynamic_table_region_data_validity(dynamic_table_region) == InspectorMessage(
            message=(
                "Some elements of dyn_tab are out of range because they are greater than the length of the target "
                "table. Note that data should contain indices, not ids."
            ),
            importance=Importance.CRITICAL,
            check_function_name="check_dynamic_table_region_data_validity",
            object_type="DynamicTableRegion",
            object_name="dyn_tab",
            location="/",
        )

    def test_pass_check_dynamic_table_region_data(self):
        dynamic_table_region = DynamicTableRegion(name="dyn_tab", description="desc", data=[0, 1, 2], table=self.table)

        assert check_dynamic_table_region_data_validity(dynamic_table_region) is None


def test_check_empty_table_with_data():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column=1)

    assert check_empty_table(table=table) is None


def test_check_empty_table_without_data():
    assert check_empty_table(table=DynamicTable(name="test_table", description="")) == InspectorMessage(
        message="This table has no data added to it.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_empty_table",
        object_type="DynamicTable",
        object_name="test_table",
        location="/",
    )


def test_check_time_interval_time_columns():
    time_intervals = TimeIntervals(name="test_table", description="desc")
    time_intervals.add_row(start_time=2.0, stop_time=3.0)
    time_intervals.add_row(start_time=1.0, stop_time=2.0)

    assert check_time_interval_time_columns(time_intervals) == InspectorMessage(
        message=(
            "['start_time'] are time columns but the values are not in ascending order. "
            "All times should be in seconds with respect to the session start time."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_time_interval_time_columns",
        object_type="TimeIntervals",
        object_name="test_table",
        location="/",
    )


def test_pass_check_time_interval_time_columns():
    time_intervals = TimeIntervals(name="test_table", description="desc")
    time_intervals.add_row(start_time=1.0, stop_time=2.0)
    time_intervals.add_row(start_time=2.0, stop_time=3.0)

    assert check_time_interval_time_columns(time_intervals) is None


def test_check_time_intervals_stop_after_start():
    time_intervals = TimeIntervals(name="test_table", description="desc")
    time_intervals.add_row(start_time=2.0, stop_time=1.5)
    time_intervals.add_row(start_time=3.0, stop_time=1.5)

    assert check_time_intervals_stop_after_start(time_intervals) == InspectorMessage(
        message=(
            "stop_times should be greater than start_times. Make sure the stop times are with respect to the "
            "session start time."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_time_intervals_stop_after_start",
        object_type="TimeIntervals",
        object_name="test_table",
        location="/",
    )


def test_pass_check_time_intervals_stop_after_start():
    time_intervals = TimeIntervals(name="test_table", description="desc")
    time_intervals.add_row(start_time=2.0, stop_time=2.5)
    time_intervals.add_row(start_time=3.0, stop_time=3.5)

    assert check_time_intervals_stop_after_start(time_intervals) is None


class TestCheckBinaryColumns(TestCase):
    def setUp(self):
        self.table = DynamicTable(name="test_table", description="")

    def test_non_binary_pass(self):
        self.table.add_column(name="test_col", description="")
        for x in [1.0, 2.0, 3.0]:
            self.table.add_row(test_col=x)

        assert check_column_binary_capability(table=self.table) is None

    def test_array_of_non_binary_pass(self):
        self.table.add_column(name="test_col", description="")
        for x in [[1.0, 2.0], [2.0, 3.0], [1.0, 2.0]]:
            self.table.add_row(test_col=x)

        assert check_column_binary_capability(table=self.table) is None

    def test_jagged_array_of_non_binary_pass(self):
        self.table.add_column(name="test_col", description="", index=True)
        for x in [[1.0, 2.0], [1.0, 2.0, 3.0], [1.0, 2.0]]:
            self.table.add_row(test_col=x)

        assert check_column_binary_capability(table=self.table) is None

    def test_no_saved_bytes_pass(self):
        self.table.add_column(name="test_col", description="")
        for x in np.array([1, 0, 1, 0], dtype="uint8"):
            self.table.add_row(test_col=x)

        assert check_column_binary_capability(table=self.table) is None

    def test_binary_floats_fail(self):
        self.table.add_column(name="test_col", description="")
        for x in [1.0, 0.0, 1.0, 0.0, 1.0]:
            self.table.add_row(test_col=x)

        assert check_column_binary_capability(table=self.table) == [
            InspectorMessage(
                message=(
                    "Column 'test_col' uses 'floats' but has binary values [0. 1.]. Consider making it boolean instead "
                    "and renaming the column to start with 'is_'; doing so will save 35.00B."
                ),
                importance=Importance.BEST_PRACTICE_SUGGESTION,
                check_function_name="check_column_binary_capability",
                object_type="DynamicTable",
                object_name="test_table",
                location="/",
            )
        ]

    def test_binary_int_fail(self):
        self.table.add_column(name="test_col", description="")
        for x in [1, 0, 1, 0, 1]:
            self.table.add_row(test_col=x)
        # the default numpy int in Windows with NumPy < 2 is int32. otherwise it is int64.
        if platform.system() == "Windows" and NumpyVersion(np.__version__) < "2.0.0":
            platform_saved_bytes = "15.00B"
        else:
            platform_saved_bytes = "35.00B"

        assert check_column_binary_capability(table=self.table) == [
            InspectorMessage(
                message=(
                    "Column 'test_col' uses 'integers' but has binary values [0 1]. Consider making it boolean "
                    f"instead and renaming the column to start with 'is_'; doing so will save {platform_saved_bytes}."
                ),
                importance=Importance.BEST_PRACTICE_SUGGESTION,
                check_function_name="check_column_binary_capability",
                object_type="DynamicTable",
                object_name="test_table",
                location="/",
            )
        ]

    def test_binary_string_fail(self):
        self.table.add_column(name="test_col", description="")
        for x in ["YES", "NO", "NO", "YES"]:
            self.table.add_row(test_col=x)
        assert check_column_binary_capability(table=self.table) == [
            InspectorMessage(
                message=(
                    "Column 'test_col' uses 'strings' but has binary values ['NO' 'YES']. Consider making it boolean "
                    "instead and renaming the column to start with 'is_'; doing so will save 44.00B."
                ),
                importance=Importance.BEST_PRACTICE_SUGGESTION,
                check_function_name="check_column_binary_capability",
                object_type="DynamicTable",
                object_name="test_table",
                location="/",
            )
        ]

    def test_binary_string_pass(self):
        self.table.add_column(name="test_col", description="")
        for x in ["testing", "testingAgain", "MoreTesting", "testing"]:
            self.table.add_row(test_col=x)
        assert check_column_binary_capability(table=self.table) is None


def test_check_binary_skip_pre_defined_columns():
    units = Units()
    units.add_unit(spike_times=[0], waveform_mean=[0])
    units.add_unit(spike_times=[1], waveform_mean=[1])

    assert check_column_binary_capability(table=units) is None


def test_check_single_row_pass():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column=1)
    table.add_row(test_column=2)

    assert check_single_row(table=table) is None


def test_check_single_row_ignore_units():
    table = Units(
        name="Units",
    )  # default name when building through nwbfile
    table.add_unit(spike_times=[1, 2, 3])

    assert check_single_row(table=table) is None


def test_check_single_row_ignore_electrodes():
    table = ElectrodeTable(
        name="electrodes",
    )  # default name when building through nwbfile
    table.add_row(
        location="unknown",
        group=ElectrodeGroup(name="test_group", description="", device=Device(name="test_device"), location="unknown"),
        group_name="test_group",
    )

    assert check_single_row(table=table) is None


def test_check_single_row_fail():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column=1)

    assert check_single_row(table=table) == InspectorMessage(
        message="This table has only a single row; it may be better represented by another data type.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_single_row",
        object_type="DynamicTable",
        object_name="test_table",
        location="/",
    )


def test_check_table_values_for_dict_non_str():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column=123)

    assert check_table_values_for_dict(table=table) is None


def test_check_table_values_for_dict_pass():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column="123")

    assert check_table_values_for_dict(table=table) is None


def test_check_table_values_for_dict_fail():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column=str(dict(a=1)))

    assert check_table_values_for_dict(table=table)[0] == InspectorMessage(
        message=(
            "The column 'test_column' contains a string value that contains a dictionary! Please unpack "
            "dictionaries as additional rows or columns of the table."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_table_values_for_dict",
        object_type="DynamicTable",
        object_name="test_table",
        location="/",
    )


def test_check_table_values_for_dict_json_case_fail():
    table = DynamicTable(name="test_table", description="")
    table.add_column(name="test_column", description="")
    table.add_row(test_column=json.dumps(dict(a=1)))

    assert check_table_values_for_dict(table=table) == [
        InspectorMessage(
            message=(
                "The column 'test_column' contains a string value that contains a dictionary! Please unpack "
                "dictionaries as additional rows or columns of the table. This string is also JSON loadable, so call "
                "`json.loads(...)` on the string to unpack."
            ),
            importance=Importance.BEST_PRACTICE_VIOLATION,
            check_function_name="check_table_values_for_dict",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
        )
    ]


def test_check_col_not_nan_pass():
    table = DynamicTable(name="test_table", description="")
    for name in ["test_column_not_nan", "test_column_string"]:
        table.add_column(name=name, description="")
    table.add_row(test_column_not_nan=1.0, test_column_string="abc")

    assert check_col_not_nan(table=table) is None


def test_check_col_not_nan_fail():
    """Addition of test_integer_type included from issue 241."""
    table = DynamicTable(name="test_table", description="")
    for name in ["test_column_not_nan_1", "test_column_nan_1", "test_integer_type", "test_column_nan_2"]:
        table.add_column(name=name, description="")
    for _ in range(400):
        table.add_row(
            test_column_not_nan_1=1.0, test_column_nan_1=np.nan, test_integer_type=1, test_column_nan_2=np.nan
        )

    assert check_col_not_nan(table=table) == [
        InspectorMessage(
            message="Column 'test_column_nan_1' might have all NaN values. Consider removing it from the table.",
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_col_not_nan",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
            file_path=None,
        ),
        InspectorMessage(
            message="Column 'test_column_nan_2' might have all NaN values. Consider removing it from the table.",
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_col_not_nan",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
            file_path=None,
        ),
    ]


def test_check_col_not_nan_fail_span_all_data():
    """Addition of test_integer_type included from issue 241."""
    table = DynamicTable(name="test_table", description="")
    for name in ["test_column_not_nan_1", "test_column_nan_1", "test_integer_type", "test_column_nan_2"]:
        table.add_column(name=name, description="")
    for _ in range(180):
        table.add_row(
            test_column_not_nan_1=1.0, test_column_nan_1=np.nan, test_integer_type=1, test_column_nan_2=np.nan
        )

    assert check_col_not_nan(table=table) == [
        InspectorMessage(
            message="Column 'test_column_nan_1' has all NaN values. Consider removing it from the table.",
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_col_not_nan",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
            file_path=None,
        ),
        InspectorMessage(
            message="Column 'test_column_nan_2' has all NaN values. Consider removing it from the table.",
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_col_not_nan",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
            file_path=None,
        ),
    ]


def test_fail_check_ids_unique():
    dt = DynamicTable(name="test_table", description="test", id=[0, 0, 1, 1])

    assert check_ids_unique(dt) == InspectorMessage(
        message="This table has ids that are not unique.",
        importance=Importance.CRITICAL,
        check_function_name="check_ids_unique",
        object_type="DynamicTable",
        object_name="test_table",
        location="/",
        file_path=None,
    )


def test_pass_check_ids_unique():
    dt = DynamicTable(name="test_table", description="test", id=[0, 1])

    assert check_ids_unique(dt) is None


def test_table_time_columns_are_not_negative_fail():
    test_table = DynamicTable(name="test_table", description="test")
    test_table.add_column(name="test_time", description="")
    test_table.add_column(name="start_time", description="")
    test_table.add_column(name="stop_time", description="")
    test_table.add_row(test_time=-2.0, start_time=-1.0, stop_time=3.0)

    assert check_table_time_columns_are_not_negative(test_table) == [
        InspectorMessage(
            message="Timestamps in column test_time should not be negative."
            " It is recommended to align the `session_start_time` or `timestamps_reference_time` to be the earliest time value that occurs in the data, and shift all other signals accordingly.",
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_table_time_columns_are_not_negative",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
        ),
        InspectorMessage(
            message="Timestamps in column start_time should not be negative."
            " It is recommended to align the `session_start_time` or `timestamps_reference_time` to be the earliest time value that occurs in the data, and shift all other signals accordingly.",
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_table_time_columns_are_not_negative",
            object_type="DynamicTable",
            object_name="test_table",
            location="/",
        ),
    ]


def test_table_time_columns_are_not_negative_pass():
    test_table = DynamicTable(name="test_table", description="test")
    test_table.add_column(name="test_time", description="")
    test_table.add_row(test_time=1.0)

    assert check_table_time_columns_are_not_negative(test_table) is None
