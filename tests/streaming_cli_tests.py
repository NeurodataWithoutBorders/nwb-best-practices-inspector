"""Test the CLI calls related to streaming."""

import os
from pathlib import Path

import py
import py.path
import pytest

from nwbinspector.testing import check_streaming_tests_enabled

STREAMING_TESTS_ENABLED, DISABLED_STREAMING_TESTS_REASON = check_streaming_tests_enabled()
EXPECTED_REPORTS_FOLDER_PATH = Path(__file__).parent / "expected_reports"


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_dandiset_streaming_cli(tmpdir: py.path.local):
    tmpdir = Path(tmpdir)

    console_output_file_path = tmpdir / "test_console_output_dandiset_streaming_cli.txt"
    os.system(f"nwbinspector 000126 --stream > {console_output_file_path}")

    assert console_output_file_path.exists()

    with open(file=console_output_file_path, mode="r") as io:
        test_console_output = io.readlines()

    expected_output_file_path = EXPECTED_REPORTS_FOLDER_PATH / "000126_report.txt"
    with open(file=expected_output_file_path, mode="r") as io:
        expected_console_output = io.readlines()

    # Different platforms maybe have different indices for start and end of test reports
    report_start = test_console_output.index("0  CRITICAL\n")
    expected_report_length = 38
    report_end = report_start + expected_report_length
    assert test_console_output[report_start:report_end] == expected_console_output[14:]


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_dandiset_streaming_cli_with_version(tmpdir: py.path.local):
    tmpdir = Path(tmpdir)

    console_output_file_path = tmpdir / "test_console_output_dandiset_streaming_cli_with_version.txt"
    os.system(f"nwbinspector 000126 --version-id 0.210813.0327 --stream > {console_output_file_path}")

    assert console_output_file_path.exists()

    with open(file=console_output_file_path, mode="r") as io:
        test_console_output = io.readlines()

    expected_output_file_path = EXPECTED_REPORTS_FOLDER_PATH / "000126_report.txt"
    with open(file=expected_output_file_path, mode="r") as io:
        expected_console_output = io.readlines()

    # Different platforms maybe have different indices for start and end of test reports
    report_start = test_console_output.index("0  CRITICAL\n")
    expected_report_length = 38
    report_end = report_start + expected_report_length
    assert test_console_output[report_start:report_end] == expected_console_output[14:]


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_dandiset_streaming_cli_saved_report(tmpdir: py.path.local):
    tmpdir = Path(tmpdir)

    report_file_path = tmpdir / "test_dandiset_streaming_cli_saved_report.txt"
    console_output_file_path = tmpdir / "test_dandiset_streaming_cli_saved_report_console_output.txt"
    os.system(f"nwbinspector 000126 --stream --report-file-path {report_file_path} > {console_output_file_path}")

    assert report_file_path.exists()
    assert console_output_file_path.exists()

    with open(file=console_output_file_path, mode="r") as io:
        test_console_output = io.readlines()

    assert "Report saved to " in "".join(test_console_output[-3:])

    with open(file=report_file_path, mode="r") as io:
        test_report = io.readlines()

    expected_report_file_path = EXPECTED_REPORTS_FOLDER_PATH / "000126_report.txt"
    with open(file=expected_report_file_path, mode="r") as io:
        expected_report = io.readlines()

    # Different platforms maybe have different indices for start and end of test reports
    report_start = test_report.index("0  CRITICAL\n")
    expected_report_length = 38
    report_end = report_start + expected_report_length
    assert test_report[report_start:report_end] == expected_report[14:]


@pytest.mark.skipif(not STREAMING_TESTS_ENABLED, reason=DISABLED_STREAMING_TESTS_REASON or "")
def test_dandiset_streaming_cli_with_version_saved_report(tmpdir: py.path.local):
    tmpdir = Path(tmpdir)

    report_file_path = tmpdir / "test_dandiset_streaming_cli_with_version_saved_report.txt"
    console_output_file_path = tmpdir / "test_dandiset_streaming_cli_with_version_saved_report_console_output.txt"
    os.system(
        f"nwbinspector 000126 --version-id 0.210813.0327 --stream "
        f"--report-file-path {report_file_path} > {console_output_file_path}"
    )

    assert report_file_path.exists()
    assert console_output_file_path.exists()

    with open(file=console_output_file_path, mode="r") as io:
        test_console_output = io.readlines()

    assert "Report saved to " in "".join(test_console_output[-3:])

    with open(file=report_file_path, mode="r") as io:
        test_report = io.readlines()

    expected_report_file_path = EXPECTED_REPORTS_FOLDER_PATH / "000126_report.txt"
    with open(file=expected_report_file_path, mode="r") as io:
        expected_report = io.readlines()

    # Different platforms maybe have different indices for start and end of test reports
    report_start = test_report.index("0  CRITICAL\n")
    expected_report_length = 38
    report_end = report_start + expected_report_length
    assert test_report[report_start:report_end] == expected_report[14:]
