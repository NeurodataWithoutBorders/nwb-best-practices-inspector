"""All tests that specifically require streaming to be enabled (i.e., ROS3 version of h5py, fsspec, etc.)."""

import pytest

from nwbinspector.testing import check_hdf5_io_open, check_streaming_tests_enabled
from nwbinspector.tools import read_nwbfile

STREAMING_TESTS_ENABLED, DISABLED_STREAMING_TESTS_REASON = check_streaming_tests_enabled()
PERSISTENT_READ_NWBFILE_HDF5_EXAMPLE_HTTPS = (
    "https://dandi-api-staging-dandisets.s3.amazonaws.com/blobs/80d/80f/80d80f55-f8a1-4318-b17e-ce55f4dd2620"
)
PERSISTENT_READ_NWBFILE_HDF5_EXAMPLE_S3 = (
    "s3://dandi-api-staging-dandisets/blobs/80d/80f/80d80f55-f8a1-4318-b17e-ce55f4dd2620"
)
PERSISTENT_READ_NWBFILE_ZARR_EXAMPLE_HTTPS = (
    "https://dandi-api-staging-dandisets.s3.amazonaws.com/zarr/63f06140-8d0c-4db4-81cc-812ed4e4db03"
)
PERSISTENT_READ_NWBFILE_ZARR_EXAMPLE_S3 = "s3://dandi-api-staging-dandisets/zarr/63f06140-8d0c-4db4-81cc-812ed4e4db03"


# These will move to PyNWB when the time is right
@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_hdf5_fsspec_https():
    nwbfile = read_nwbfile(
        nwbfile_path=PERSISTENT_READ_NWBFILE_HDF5_EXAMPLE_HTTPS,
        backend="hdf5",  # TODO: cannot current auto-detect backend when streaming
        method="fsspec",
    )
    assert check_hdf5_io_open(io=nwbfile.read_io)

    nwbfile.read_io.close()
    assert not check_hdf5_io_open(io=nwbfile.read_io)


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_hdf5_fsspec_s3():
    nwbfile = read_nwbfile(
        nwbfile_path=PERSISTENT_READ_NWBFILE_HDF5_EXAMPLE_S3,
        backend="hdf5",  # TODO: cannot current auto-detect backend when streaming
        method="fsspec",
    )
    assert check_hdf5_io_open(io=nwbfile.read_io)

    nwbfile.read_io.close()
    assert not check_hdf5_io_open(io=nwbfile.read_io)


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_hdf5_ros3_https():
    nwbfile = read_nwbfile(
        nwbfile_path=PERSISTENT_READ_NWBFILE_HDF5_EXAMPLE_HTTPS,
        backend="hdf5",  # TODO: cannot current auto-detect backend when streaming
        method="ros3",
    )
    assert check_hdf5_io_open(io=nwbfile.read_io)

    nwbfile.read_io.close()
    assert not check_hdf5_io_open(io=nwbfile.read_io)


# Zarr files not working yet with streaming

# @pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
# def test_zarr_fsspec_streaming_https():
#     nwbfile = read_nwbfile(
#         nwbfile_path=PERSISTENT_READ_NWBFILE_ZARR_EXAMPLE_HTTPS,
#         method="fsspec",
#     )
#     assert check_zarr_io_open(io=nwbfile.read_io)

#     nwbfile.read_io.close()
#     assert not check_zarr_io_open(io=nwbfile.read_io)


# @pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
# def test_zarr_fsspec_streaming_s3():
#     nwbfile = read_nwbfile(
#         nwbfile_path=PERSISTENT_READ_NWBFILE_ZARR_EXAMPLE_S3,
#         method="fsspec",
#     )
#     assert check_zarr_io_open(io=nwbfile.read_io)

#     nwbfile.read_io.close()
#     assert not check_zarr_io_open(io=nwbfile.read_io)


# @pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
# def test_zarr_ros3_error():
#     test that an error is raised with ros3 driver on zarr (not applicable)
