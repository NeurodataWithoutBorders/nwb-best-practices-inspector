import numpy as np
from pynwb.behavior import CompassDirection, SpatialSeries

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import (
    check_compass_direction_unit,
    check_spatial_series_degrees_magnitude,
    check_spatial_series_dims,
    check_spatial_series_radians_magnitude,
)


def test_check_spatial_series_dims():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10, 4)),
        rate=3.0,
        reference_frame="reference_frame",
    )
    assert check_spatial_series_dims(spatial_series) == InspectorMessage(
        message="SpatialSeries should have 1 column (x), 2 columns (x, y), or 3 columns (x, y, z).",
        importance=Importance.CRITICAL,
        check_function_name="check_spatial_series_dims",
        object_type="SpatialSeries",
        object_name="SpatialSeries",
        location="/",
    )


def test_pass_check_spatial_series_dims():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10, 3)),
        rate=3.0,
        reference_frame="reference_frame",
    )

    assert check_spatial_series_dims(spatial_series) is None


def test_pass_check_spatial_series_dims_1d():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10,)),
        rate=3.0,
        reference_frame="reference_frame",
    )

    assert check_spatial_series_dims(spatial_series) is None


def test_trigger_check_compass_direction_unit():
    obj = CompassDirection(
        spatial_series=SpatialSeries(
            name="SpatialSeries",
            description="description",
            data=np.ones((10,)),
            rate=3.0,
            reference_frame="reference_frame",
        )
    )

    assert (
        check_compass_direction_unit(obj)[0].message == "SpatialSeries objects inside a CompassDirection object "
        "should be angular and should have a unit of 'degrees' or 'radians', but 'SpatialSeries' has units 'meters'."
    )


def test_pass_check_compass_direction_unit():
    for unit in ("radians", "degrees"):
        obj = CompassDirection(
            spatial_series=SpatialSeries(
                name="SpatialSeries",
                description="description",
                data=np.ones((10,)),
                rate=3.0,
                reference_frame="reference_frame",
                unit=unit,
            )
        )

        assert check_compass_direction_unit(obj) is None


def test_pass_check_spatial_series_degrees_magnitude():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10,)),
        rate=3.0,
        reference_frame="reference_frame",
        unit="degrees",
    )

    assert check_spatial_series_degrees_magnitude(spatial_series) is None


def test_check_spatial_series_degrees_magnitude():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10,)) * 400,
        rate=3.0,
        reference_frame="reference_frame",
        unit="degrees",
    )

    assert check_spatial_series_degrees_magnitude(spatial_series) == InspectorMessage(
        check_function_name="check_spatial_series_degrees_magnitude",
        message="SpatialSeries with units of degrees must have values between -360 and 360.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        object_name="SpatialSeries",
        location="/",
        object_type="SpatialSeries",
    )


def test_pass_check_spatial_series_radians_magnitude():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10,)),
        rate=3.0,
        reference_frame="reference_frame",
        unit="radians",
    )

    assert check_spatial_series_radians_magnitude(spatial_series) is None


def test_check_spatial_series_radians_magnitude():
    spatial_series = SpatialSeries(
        name="SpatialSeries",
        description="description",
        data=np.ones((10,)) * 400,
        rate=3.0,
        reference_frame="reference_frame",
        unit="radians",
    )

    assert check_spatial_series_radians_magnitude(spatial_series) == InspectorMessage(
        check_function_name="check_spatial_series_radians_magnitude",
        message="SpatialSeries with units of radians must have values between -2pi and 2pi.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        object_name="SpatialSeries",
        location="/",
        object_type="SpatialSeries",
    )
