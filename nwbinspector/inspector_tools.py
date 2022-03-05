"""Internally used tools specifically for rendering more human-readable output from collected check results."""
import sys
import os
from enum import Enum
from collections import OrderedDict
from typing import Dict, List
from pathlib import Path

import numpy as np

from .register_checks import Importance
from .utils import FilePathType


def sort_by_descending_severity(check_results: list):
    """Order the dictionaries in the check_list by severity."""
    severities = [check_result.severity.value for check_result in check_results]
    descending_indices = np.argsort(severities)[::-1]
    return [check_results[j] for j in descending_indices]


def organize_check_results(check_results: list):
    """Format the list of returned results from checks."""
    initial_results = OrderedDict({importance.name: list() for importance in Importance})
    for check_result in check_results:
        initial_results[check_result.importance.name].append(check_result)
    organized_check_results = OrderedDict()
    for importance_level, check_results in initial_results.items():
        if any(check_results):
            organized_check_results.update({importance_level: sort_by_descending_severity(check_results=check_results)})
    return organized_check_results


def format_organized_results_output(organized_results: Dict[str, Dict[str, list]]) -> List[str]:
    """Convert organized_results structure into list of strings ready for console output or file write."""
    num_nwbfiles = len(organized_results)
    formatted_output = list()
    for nwbfile_index, (nwbfile_name, organized_check_results) in enumerate(organized_results.items(), start=1):
        nwbfile_name_string = f"NWBFile: {nwbfile_name}"
        formatted_output.append(nwbfile_name_string + "\n")
        formatted_output.append("=" * len(nwbfile_name_string) + "\n")

        for importance_index, (importance_level, check_results) in enumerate(organized_check_results.items(), start=1):
            importance_string = importance_level.name.replace("_", " ")
            formatted_output.append(f"\n{importance_string}\n")
            formatted_output.append("-" * len(importance_string) + "\n")

            if importance_level in ["ERROR", "PYNWB_VALIDATION"]:
                for check_index, check_result in enumerate(check_results, start=1):
                    formatted_output.append(
                        f"{nwbfile_index}.{importance_index}.{check_index}   {check_result.object_type} "
                        f"'{check_result.location}': {check_result.check_function_name}: {check_result.message}\n"
                    )
            else:
                for check_index, check_result in enumerate(check_results, start=1):
                    formatted_output.append(
                        f"{nwbfile_index}.{importance_index}.{check_index}   {check_result.object_type} "
                        f"'{check_result.object_name}' located in '{check_result.location}'\n"
                        f"        {check_result.check_function_name}: {check_result.message}\n"
                    )
        if nwbfile_index != num_nwbfiles:
            formatted_output.append("\n\n\n")
    return formatted_output


def supports_color():  # pragma: no cover
    """
    Return True if the running system's terminal supports color, and False otherwise.

    From https://github.com/django/django/blob/main/django/core/management/color.py
    """

    def vt_codes_enabled_in_windows_registry():
        """Check the Windows Registry to see if VT code handling has been enabled by default."""
        try:
            # winreg is only available on Windows.
            import winreg
        except ImportError:
            return False
        else:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
            try:
                reg_key_value, _ = winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
            except FileNotFoundError:
                return False
            else:
                return reg_key_value == 1

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    return is_a_tty and (
        sys.platform != "win32"
        or "ANSICON" in os.environ
        or "WT_SESSION" in os.environ  # Windows Terminal supports VT codes.
        or os.environ.get("TERM_PROGRAM") == "vscode"  # Microsoft Visual Studio Code's built-in terminal.
        or vt_codes_enabled_in_windows_registry()
    )


def wrap_color(formatted_results: List[str], no_color: bool = False):  # pragma: no cover
    """Wrap the file output with colors for console output."""
    if not supports_color():
        return formatted_results
    reset_color = "\x1b[0m"
    color_map = {
        "CRITICAL IMPORTANCE": "\x1b[31m",
        "BEST PRACTICE VIOLATION": "\x1b[33m",
        "BEST PRACTICE SUGGESTION": reset_color,
        "NWBFile": reset_color,
    }

    color_shift_points = dict()
    for line_index, line in enumerate(formatted_results):
        for color_trigger in color_map:
            if color_trigger in line:
                color_shift_points.update(
                    {line_index: color_map[color_trigger], line_index + 1: color_map[color_trigger]}
                )
    colored_output = list()
    current_color = None
    for line in formatted_results:
        transition_point = line_index in color_shift_points
        if transition_point:
            current_color = color_shift_points[line_index]
            colored_output.append(f"{current_color}{line}{reset_color}")
        if current_color is not None and not transition_point:
            colored_output.append(f"{current_color}{line[:6]}{reset_color}{line[6:]}")


def print_to_console(formatted_results: List[str], no_color: bool = False):
    """Print log file contents to console."""
    wrap_color(formatted_results=formatted_results, no_color=no_color)
    sys.stdout.write(os.linesep * 2)
    for line in formatted_results:
        sys.stdout.write(line)


def save_report(report_file_path: FilePathType, formatted_results: List[str], overwrite=False):
    """Write the list of organized check results to a nicely formatted text file."""
    report_file_path = Path(report_file_path)
    if report_file_path.exists() and not overwrite:
        raise FileExistsError(f"The file {report_file_path} already exists! Set 'overwrite=True' or pass '-o' flag.")
    with open(file=report_file_path, mode="w", newline="\n") as file:
        for line in formatted_results:
            file.write(line)
