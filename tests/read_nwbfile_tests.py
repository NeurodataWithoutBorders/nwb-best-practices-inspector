"""Temporary tests for thorough testing and evaluation of the proposed `read_nwbfile` helper function."""

from pathlib import Path

import pytest
from hdmf_zarr import NWBZarrIO
from pynwb import NWBHDF5IO
from pynwb.testing.mock.base import mock_TimeSeries
from pynwb.testing.mock.file import mock_NWBFile

from nwbinspector.testing import (
    check_hdf5_io_open,
    check_streaming_tests_enabled,
    check_zarr_io_open,
)
from nwbinspector.tools import read_nwbfile

STREAMING_TESTS_ENABLED, DISABLED_STREAMING_TESTS_REASON = check_streaming_tests_enabled()


@pytest.fixture(scope="session")
def hdf5_nwbfile_path(tmpdir_factory):
    nwbfile_path = tmpdir_factory.mktemp("data").join("test_read_nwbfile_hdf5.nwb")
    if not Path(nwbfile_path).exists():
        nwbfile = mock_NWBFile()
        nwbfile.add_acquisition(mock_TimeSeries())
        with NWBHDF5IO(path=str(nwbfile_path), mode="w") as io:
            io.write(nwbfile)
    return nwbfile_path


@pytest.fixture(scope="session")
def zarr_nwbfile_path(tmpdir_factory):
    nwbfile_path = tmpdir_factory.mktemp("data").join("test_read_nwbfile_zarr.nwb")
    if not Path(nwbfile_path).exists():
        nwbfile = mock_NWBFile()
        nwbfile.add_acquisition(mock_TimeSeries())
        with NWBZarrIO(path=str(nwbfile_path), mode="w") as io:
            io.write(nwbfile)
    return nwbfile_path


# Assertion tests
def test_incorrect_backend_set_on_hdf5(hdf5_nwbfile_path):
    with pytest.raises(IOError) as excinfo:
        read_nwbfile(nwbfile_path=hdf5_nwbfile_path, backend="zarr")
    assert "The chosen backend (zarr) is unable to read the file! Please select a different backend." in str(
        excinfo.value
    )


def test_incorrect_backend_set_on_zarr(zarr_nwbfile_path):
    with pytest.raises(IOError) as excinfo:
        read_nwbfile(nwbfile_path=zarr_nwbfile_path, backend="hdf5")
    assert "The chosen backend (hdf5) is unable to read the file! Please select a different backend." in str(
        excinfo.value
    )


def test_incorrect_method_set_on_hdf5(hdf5_nwbfile_path):
    with pytest.raises(ValueError) as excinfo:
        read_nwbfile(nwbfile_path=hdf5_nwbfile_path, method="fsspec")
    assert (
        f"The file ({hdf5_nwbfile_path}) is a local path on your system, but the method (fsspec) was selected! "
        "Please set method='local'."
    ) in str(excinfo.value)


def test_incorrect_method_set_on_remote_hdf5():
    nwbfile_path = (
        "https://dandi-api-staging-dandisets.s3.amazonaws.com/blobs/6a6/1ba/6a61bab5-0662-49e5-be46-0b9ee9a27297"
    )

    with pytest.raises(ValueError) as excinfo:
        read_nwbfile(
            nwbfile_path=nwbfile_path,
            backend="hdf5",  # Currently unable to auto-determine backend with https
            method="local",
        )
    assert (
        f"The path ({nwbfile_path}) is an external URL, but the method (local) was selected! "
        "Please set method='fsspec' or 'ros3' (for HDF5 only)."
    ) in str(excinfo.value)


def test_s3_url_set_on_ros3_hdf5():
    nwbfile_path = "s3://dandi-api-staging-dandisets/blobs/80d/80f/80d80f55-f8a1-4318-b17e-ce55f4dd2620"
    with pytest.raises(ValueError) as excinfo:
        read_nwbfile(
            nwbfile_path=nwbfile_path,
            backend="hdf5",
            method="ros3",
        )
    assert "The ROS3 method was selected, but the URL starts with 's3://'! Please switch to an 'https://' URL." in str(
        excinfo.value
    )


# HDF5 tests
def test_hdf5_explicit_closure(hdf5_nwbfile_path):
    nwbfile = read_nwbfile(nwbfile_path=hdf5_nwbfile_path)
    assert check_hdf5_io_open(io=nwbfile.read_io)

    nwbfile.read_io.close()
    assert not check_hdf5_io_open(io=nwbfile.read_io)


def test_hdf5_object_deletion_does_not_close_io(hdf5_nwbfile_path):
    """Deleting the `nwbfile` object should not trigger `io.close` if `io` is still being referenced independently."""
    nwbfile = read_nwbfile(nwbfile_path=hdf5_nwbfile_path)
    io = nwbfile.read_io  # keep reference in namespace so it persists after nwbfile deletion
    assert check_hdf5_io_open(io=io)

    del nwbfile
    assert check_hdf5_io_open(io=io)


def test_hdf5_object_replacement_does_not_close_io(hdf5_nwbfile_path):
    """Deleting the `nwbfile` object should not trigger `io.close` if `io` is still being referenced independently."""
    nwbfile_1 = read_nwbfile(nwbfile_path=hdf5_nwbfile_path)
    io_1 = nwbfile_1.read_io
    assert check_hdf5_io_open(io=io_1)

    nwbfile_2 = read_nwbfile(nwbfile_path=hdf5_nwbfile_path)
    io_2 = nwbfile_2.read_io
    assert check_hdf5_io_open(io=io_2)

    nwbfile_2 = nwbfile_1
    assert check_hdf5_io_open(io=io_1)
    assert check_hdf5_io_open(io=io_2)


# Zarr tests
def test_zarr_explicit_closure(zarr_nwbfile_path):
    nwbfile = read_nwbfile(nwbfile_path=zarr_nwbfile_path)
    assert check_zarr_io_open(io=nwbfile.read_io)

    nwbfile.read_io.close()
    assert not check_zarr_io_open(io=nwbfile.read_io)


def test_zarr_object_deletion_does_not_close_io(zarr_nwbfile_path):
    """Deleting the `nwbfile` object should not trigger `io.close` if `io` is still being referenced independently."""
    nwbfile = read_nwbfile(nwbfile_path=zarr_nwbfile_path)
    io = nwbfile.read_io  # keep reference in namespace so it persists after nwbfile deletion
    assert check_zarr_io_open(io=io)

    del nwbfile
    assert check_zarr_io_open(io=io)


def test_zarr_object_replacement_does_not_close_io(zarr_nwbfile_path):
    """Deleting the `nwbfile` object should not trigger `io.close` if `io` is still being referenced independently."""
    nwbfile_1 = read_nwbfile(nwbfile_path=zarr_nwbfile_path)
    io_1 = nwbfile_1.read_io
    assert check_zarr_io_open(io=io_1)

    nwbfile_2 = read_nwbfile(nwbfile_path=zarr_nwbfile_path)
    io_2 = nwbfile_2.read_io
    assert check_zarr_io_open(io=io_2)

    nwbfile_2 = nwbfile_1
    assert check_zarr_io_open(io=io_1)
    assert check_zarr_io_open(io=io_2)
