import os

import numpy as np
import pytest
from hdmf.testing import TestCase
from packaging import version

from nwbinspector import Importance
from nwbinspector.utils import (
    calculate_number_of_cpu,
    format_byte_size,
    get_package_version,
    is_ascending_series,
    is_dict_in_string,
    is_regular_series,
    strtobool,
)


def test_format_byte_size():
    assert format_byte_size(byte_size=12345) == "12.35KB"


def test_format_byte_size_in_binary():
    assert format_byte_size(byte_size=12345, units="binary") == "12.06KiB"


class TestFormatByteException(TestCase):
    def test_format_byte_size_units_exception(self):
        with self.assertRaisesWith(
            exc_type=ValueError,
            exc_msg="'units' argument must be either 'SI' (for orders of 1000) or 'binary' (for orders of 1024).",
        ):
            format_byte_size(byte_size=12345, units="test")


def test_is_regular_series():
    assert is_regular_series(series=[1, 2, 3])
    assert not is_regular_series(series=[1, 2, 4])


def test_is_dict_in_string_false_1():
    string = "not a dict"
    assert is_dict_in_string(string=string) is False


def test_is_dict_in_string_false_2():
    string = "not a dict, {but also fancy format text!}"
    assert is_dict_in_string(string=string) is False


def test_is_dict_in_string_false_3():
    string = "[not] a dict, {[but] also} fancy format text!"
    assert is_dict_in_string(string=string) is False


def test_is_dict_in_string_true_1():
    string = str(dict(a=1))
    assert is_dict_in_string(string=string) is True


def test_is_dict_in_string_true_2():
    string = str([dict(a=1), dict(b=2)])
    assert is_dict_in_string(string=string) is True


def test_is_dict_in_string_true_3():
    string = str(dict(a=dict(b=2)))
    assert is_dict_in_string(string=string) is True


def test_is_dict_in_string_true_4():
    string = "some text: {'then': 'a dict'}"
    assert is_dict_in_string(string=string) is True


def test_is_dict_in_string_true_5():
    string = "{'then': 'a dict'} more text"
    assert is_dict_in_string(string=string) is True


def test_is_dict_in_string_true_6():
    """Not a JSON encodable object."""
    string = str({1.2: Importance.CRITICAL})
    assert is_dict_in_string(string=string) is True


def test_is_dict_in_string_true_7():
    """
    A more aggressive demonstration of the general dictionary regex.

    But it is technically possible to achieve via `str({custom_object_1: custom_object_2})` if 'custom_object_1' is
    hashable and both custom objects have manual `__repr__` that do not include apostrophe's within their return.

    Example
    -------
    from dataclasses import dataclass

    @dataclass
    class Test():
        prop = 1

        def __repr__(self):
            return "This is a test"

    str({1: Test()})
    """
    string = "example, {this is not a dict: but it sure looks like one}!"
    assert is_dict_in_string(string=string) is True


def test_get_package_version_type():
    assert isinstance(get_package_version("hdmf"), version.Version)


def test_get_package_version_value():
    assert get_package_version("hdmf") >= version.parse("3.1.1")  # minimum supported PyNWB version


class TestCalulcateNumberOfCPU(TestCase):
    total_cpu = os.cpu_count()

    def test_request_more_than_available_assert(self):
        requested_cpu = 2500
        with self.assertRaisesWith(
            exc_type=AssertionError,
            exc_msg=f"Requested more CPUs ({requested_cpu}) than are available ({self.total_cpu})!",
        ):
            calculate_number_of_cpu(requested_cpu=requested_cpu)

    def test_request_fewer_than_available_assert(self):
        requested_cpu = -2500
        with self.assertRaisesWith(
            exc_type=AssertionError,
            exc_msg=f"Requested fewer CPUs ({requested_cpu}) than are available ({self.total_cpu})!",
        ):
            calculate_number_of_cpu(requested_cpu=requested_cpu)

    def test_calculate_number_of_cpu_negative_value(self):
        requested_cpu = -1  # CI only has 2 jobs available
        assert calculate_number_of_cpu(requested_cpu=requested_cpu) == requested_cpu % self.total_cpu


def test_is_ascending_series():
    assert is_ascending_series(series=[1, 1, 1])
    assert is_ascending_series(series=[1, 2, 3])
    assert is_ascending_series(series=[1, np.nan, 3])
    assert not is_ascending_series(series=[1, 2, 1])


@pytest.mark.parametrize(
    "values,target",
    [
        (("y", "yes", "t", "true", "on", "1"), True),
        (("n", "no", "f", "false", "off", "0"), False),
    ],
)
def test_strtobool(values, target):
    for v in values:
        assert strtobool(v) is target
        assert strtobool(v.upper()) is target
        with pytest.raises(ValueError):
            strtobool(v + "1")
    # it is strtobool, so no bool is allowed
    with pytest.raises(TypeError):
        strtobool(target)
