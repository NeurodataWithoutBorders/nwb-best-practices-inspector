"""Test the API functions related to streaming."""

import pytest

from nwbinspector import (
    Importance,
    InspectorMessage,
    inspect_all,
    inspect_dandi_file_path,
    inspect_dandiset,
    inspect_url,
)
from nwbinspector.testing import check_streaming_tests_enabled

STREAMING_TESTS_ENABLED, DISABLED_STREAMING_TESTS_REASON = check_streaming_tests_enabled()


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_inspect_all_streaming():
    dandiset_id = "000126"
    select = ["check_subject_species_exists"]

    test_messages = list(inspect_all(path=dandiset_id, stream=True, select=select))
    assert len(test_messages) == 1

    test_message = test_messages[0]
    expected_message = InspectorMessage(
        message="Subject species is missing.",
        importance=Importance.CRITICAL,  # Uses dandi config by default
        check_function_name="check_subject_species_exists",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
        file_path="sub-1/sub-1.nwb",
    )

    assert test_message == expected_message


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_inspect_dandiset():
    dandiset_id = "000126"
    select = ["check_subject_species_exists"]

    test_messages = list(inspect_dandiset(dandiset_id=dandiset_id, select=select))
    assert len(test_messages) == 1

    test_message = test_messages[0]
    expected_message = InspectorMessage(
        message="Subject species is missing.",
        importance=Importance.CRITICAL,  # Uses dandi config by default
        check_function_name="check_subject_species_exists",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
        file_path="sub-1/sub-1.nwb",
    )

    assert test_message == expected_message


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_inspect_dandi_file_path():
    dandiset_id = "000126"
    dandi_file_path = "sub-1/sub-1.nwb"
    select = ["check_subject_species_exists"]

    test_messages = list(
        inspect_dandi_file_path(dandi_file_path=dandi_file_path, dandiset_id=dandiset_id, select=select)
    )
    assert len(test_messages) == 1

    test_message = test_messages[0]
    expected_message = InspectorMessage(
        message="Subject species is missing.",
        importance=Importance.CRITICAL,  # Uses dandi config by default
        check_function_name="check_subject_species_exists",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
        file_path=dandi_file_path,
    )

    assert test_message == expected_message


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_inspect_url():
    url = "https://dandiarchive.s3.amazonaws.com/blobs/11e/c89/11ec8933-1456-4942-922b-94e5878bb991"
    select = ["check_subject_species_exists"]

    test_messages = list(inspect_url(url=url, select=select))
    assert len(test_messages) == 1

    test_message = test_messages[0]
    expected_message = InspectorMessage(
        message="Subject species is missing.",
        importance=Importance.CRITICAL,  # Uses dandi config by default
        check_function_name="check_subject_species_exists",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
        file_path=url,
    )

    assert test_message == expected_message
