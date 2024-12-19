import h5py
import pynwb
import pytest
import numpy as np
from packaging import version


from nwbinspector import (
    InspectorMessage,
    Importance,
    check_regular_timestamps,
    check_data_orientation,
    check_timestamps_match_first_dimension,
    check_timestamps_ascending,
    check_missing_unit,
    check_resolution,
    check_timestamp_of_the_first_sample_is_not_negative,
    check_rate_is_not_zero,
)
from nwbinspector.tools import make_minimal_nwbfile
from nwbinspector.testing import check_streaming_tests_enabled
from nwbinspector.utils import get_package_version, robust_s3_read

STREAMING_TESTS_ENABLED, DISABLED_STREAMING_TESTS_REASON = check_streaming_tests_enabled()


def test_check_regular_timestamps():
    assert check_regular_timestamps(
        time_series=pynwb.TimeSeries(
            name="test_time_series",
            unit="test_units",
            data=np.zeros(shape=3),
            timestamps=[1.2, 3.2, 5.2],
        )
    ) == InspectorMessage(
        message=(
            "TimeSeries appears to have a constant sampling rate. Consider specifying starting_time=1.2 and rate=2.0 "
            "instead of timestamps."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_regular_timestamps",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_pass_check_regular_timestamps():
    """Should pass because there are only two timestamps"""
    assert (
        check_regular_timestamps(
            time_series=pynwb.TimeSeries(
                name="test_time_series",
                unit="test_units",
                data=[0, 0],
                timestamps=[1.2, 3.2],
            )
        )
        is None
    )


def test_check_data_orientation():
    assert check_data_orientation(
        time_series=pynwb.TimeSeries(
            name="test_time_series",
            unit="test_units",
            data=np.zeros(shape=(2, 100)),
            rate=1.0,
        )
    ) == InspectorMessage(
        message=(
            "Data may be in the wrong orientation. "
            "Time should be in the first dimension, and is usually the longest dimension. "
            "Here, another dimension is longer."
        ),
        importance=Importance.CRITICAL,
        check_function_name="check_data_orientation",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_data_orientation_unbounded_maxshape(tmp_path):
    filepath = tmp_path / "test.nwb"
    with h5py.File(filepath, "w") as file:
        data = file.create_dataset(
            "data",
            data=np.ones((10, 3)),
            maxshape=(None, 3),
        )

        time_series = pynwb.TimeSeries(
            name="test_time_series",
            unit="test_units",
            data=data,
            rate=1.0,
        )

        assert check_data_orientation(time_series) is None


def test_check_timestamps_match_first_dimension_good():
    assert (
        check_timestamps_match_first_dimension(
            time_series=pynwb.TimeSeries(
                name="test_time_series",
                unit="test_units",
                data=np.empty(shape=4),
                timestamps=[1.0, 2.0, 3.0, 4.0],
            )
        )
        is None
    )


def test_check_timestamps_match_first_dimension_special_skip(tmp_path):
    """
    Very special skip condition for a certain older practice for indexing repeated Images.

    The use of an ImageSeries for this is discouraged, with preference to use a stack of unordered Images instead.
    """
    nwbfile_path = tmp_path / "test_check_timestamps_match_first_dimension_special_skip.nwb"

    nwbfile = make_minimal_nwbfile()
    num_images = 5
    image_width = 10
    image_height = 15
    num_channels = 3
    dtype = "uint8"
    image_series = pynwb.image.ImageSeries(
        name="ImageSeries",
        unit="n.a.",
        data=np.empty(shape=(num_images, image_width, image_height, num_channels), dtype=dtype),
        timestamps=[],
    )
    nwbfile.add_acquisition(image_series)
    nwbfile.add_acquisition(
        pynwb.image.IndexSeries(
            name="IndexSeries",
            unit="n.a.",
            data=[0, 1],
            indexed_timeseries=image_series,
            timestamps=[0.5, 0.6],
        )
    )

    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as io:
        io.write(nwbfile)

    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="r") as io:
        nwbfile_out = io.read()
        image_series_out = nwbfile_out.acquisition["ImageSeries"]

        assert check_timestamps_match_first_dimension(time_series=image_series_out) is None


def test_check_timestamps_match_first_dimension_bad():
    assert check_timestamps_match_first_dimension(
        time_series=pynwb.TimeSeries(
            name="test_time_series",
            unit="test_units",
            data=np.empty(shape=4),
            timestamps=[1.0, 2.0, 3.0],
        )
    ) == InspectorMessage(
        message="The length of the first dimension of data (4) does not match the length of timestamps (3).",
        importance=Importance.CRITICAL,
        check_function_name="check_timestamps_match_first_dimension",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_timestamps_empty_data():
    assert check_timestamps_match_first_dimension(
        time_series=pynwb.TimeSeries(name="test_time_series", unit="test_units", data=[], timestamps=[1.0, 2.0, 3.0])
    ) == InspectorMessage(
        message="The length of the first dimension of data (0) does not match the length of timestamps (3).",
        importance=Importance.CRITICAL,
        check_function_name="check_timestamps_match_first_dimension",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_timestamps_empty_timestamps():
    assert check_timestamps_match_first_dimension(
        time_series=pynwb.TimeSeries(name="test_time_series", unit="test_units", data=np.empty(shape=4), timestamps=[])
    ) == InspectorMessage(
        message="The length of the first dimension of data (4) does not match the length of timestamps (0).",
        importance=Importance.CRITICAL,
        check_function_name="check_timestamps_match_first_dimension",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_rate_is_not_zero_pass():
    time_series = pynwb.TimeSeries(name="test", unit="test_units", data=[1, 2, 3], rate=4.0)
    assert check_rate_is_not_zero(time_series) is None


def test_check_rate_is_not_zero_single_frame_pass():
    time_series = pynwb.TimeSeries(name="test", unit="test_units", data=[1], rate=0.0)
    assert check_rate_is_not_zero(time_series) is None


def test_check_rate_is_not_zero_fail():
    time_series = pynwb.TimeSeries(name="TimeSeriesTest", unit="n.a.", data=[1, 2, 3], rate=0.0)
    assert check_rate_is_not_zero(time_series) == InspectorMessage(
        message="TimeSeriesTest has a sampling rate value of 0.0Hz but the series has more than one frame.",
        importance=Importance.CRITICAL,
        check_function_name="check_rate_is_not_zero",
        object_type="TimeSeries",
        object_name="TimeSeriesTest",
        location="/",
    )


def test_pass_check_timestamps_ascending_pass():
    time_series = pynwb.TimeSeries(name="test_time_series", unit="test_units", data=[1, 2, 3], timestamps=[1, 2, 3])
    assert check_timestamps_ascending(time_series) is None


def test_check_timestamps_ascending_fail():
    time_series = pynwb.TimeSeries(name="test_time_series", unit="test_units", data=[1, 2, 3], timestamps=[1, 3, 2])
    assert check_timestamps_ascending(time_series) == InspectorMessage(
        message="test_time_series timestamps are not ascending.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_timestamps_ascending",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_timestamp_of_the_first_sample_is_not_negative_with_timestamps_fail():
    time_series = pynwb.TimeSeries(name="test_time_series", unit="test_units", data=[1, 2, 3], timestamps=[-1, 0, 1])
    message = (
        "Timestamps should not be negative. This usually indicates a temporal misalignment of the data. "
        " It is recommended to align the `session_start_time` or `timestamps_reference_time` to be the earliest time value that occurs in the data, and shift all other signals accordingly."            
    )
    assert check_timestamp_of_the_first_sample_is_not_negative(time_series) == InspectorMessage(
        message=message,
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_timestamp_of_the_first_sample_is_not_negative",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_timestamp_of_the_first_sample_is_not_negative_with_timestamps_pass():
    time_series = pynwb.TimeSeries(name="test_time_series", unit="test_units", data=[1, 2, 3], timestamps=[0, 1, 2])
    assert check_timestamp_of_the_first_sample_is_not_negative(time_series) is None


def test_check_timestamp_of_the_first_sample_is_not_negative_with_starting_time_fail():
    time_series = pynwb.TimeSeries(
        name="test_time_series", unit="test_units", data=[1, 2, 3], starting_time=-1.0, rate=30.0
    )
    message = (
        "Timestamps should not be negative."
        " It is recommended to align the `session_start_time` or `timestamps_reference_time` "
        "to be the earliest time value that occurs in the data, and shift all other signals accordingly."
    )
    assert check_timestamp_of_the_first_sample_is_not_negative(time_series) == InspectorMessage(
        message=message,
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_timestamp_of_the_first_sample_is_not_negative",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_timestamp_of_the_first_sample_is_not_negative_with_starting_time_pass():
    time_series = pynwb.TimeSeries(
        name="test_time_series", unit="test_units", data=[1, 2, 3], starting_time=0.0, rate=30.0
    )
    assert check_timestamp_of_the_first_sample_is_not_negative(time_series) is None


def test_check_missing_unit_pass():
    time_series = pynwb.TimeSeries(name="test_time_series", unit="test_units", data=[1, 2, 3], timestamps=[1, 2, 3])
    assert check_missing_unit(time_series) is None


def test_check_missing_unit_fail():
    time_series = pynwb.TimeSeries(name="test_time_series", unit="", data=[1, 2, 3], timestamps=[1, 2, 3])
    assert check_missing_unit(time_series) == InspectorMessage(
        message="Missing text for attribute 'unit'. Please specify the scientific unit of the 'data'.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_missing_unit",
        object_type="TimeSeries",
        object_name="test_time_series",
        location="/",
    )


def test_check_positive_resolution_pass():
    time_series = pynwb.TimeSeries(name="test", unit="test_units", data=[1, 2, 3], timestamps=[1, 2, 3], resolution=3.4)
    assert check_resolution(time_series) is None


def test_check_unknown_resolution_pass():
    for valid_unknown in [-1.0, np.nan]:
        time_series = pynwb.TimeSeries(name="test", unit="test", data=[1], timestamps=[1], resolution=valid_unknown)
        assert check_resolution(time_series) is None


@pytest.mark.skipif(
    not STREAMING_TESTS_ENABLED or get_package_version("hdmf") >= version.parse("3.3.1"),
    reason=f"{DISABLED_STREAMING_TESTS_REASON or ''}. Also needs 'hdmf<3.3.1'.",
)
def test_check_none_matnwb_resolution_pass():
    """
    Special test on the original problematic file found at

    https://dandiarchive.org/dandiset/000065/draft/files?location=sub-Kibbles%2F

    produced with MatNWB, when read with PyNWB~=2.0.1 and HDMF<=3.2.1 contains a resolution value of None.
    """
    with pynwb.NWBHDF5IO(
        path="https://dandiarchive.s3.amazonaws.com/blobs/da5/107/da510761-653e-4b81-a330-9cdae4838180",
        mode="r",
        load_namespaces=True,
        driver="ros3",
    ) as io:
        nwbfile = robust_s3_read(command=io.read)
        time_series = robust_s3_read(
            command=nwbfile.processing["video_files"]["video"].time_series.get,
            command_args=["20170203_KIB_01_s1.1.h264"],
        )
    assert check_resolution(time_series) is None


def test_check_resolution_fail():
    time_series = pynwb.TimeSeries(name="test", unit="test", data=[1, 2, 3], timestamps=[1, 2, 3], resolution=-2.0)
    assert check_resolution(time_series) == InspectorMessage(
        message="'resolution' should use -1.0 or NaN for unknown instead of -2.0.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_resolution",
        object_type="TimeSeries",
        object_name="test",
        location="/",
    )
