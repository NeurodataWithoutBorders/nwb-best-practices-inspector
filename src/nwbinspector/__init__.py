import importlib.metadata

from ._registration import available_checks, register_check
from ._types import Importance, Severity, InspectorMessage
from ._configuration import load_config, validate_config, configure_checks
from ._nwb_inspection import (
    inspect_all,
    inspect_nwbfile,
    inspect_nwbfile_object,
    run_checks,
)
from ._formatting import (
    format_messages,
    print_to_console,
    save_report,
    MessageFormatter,
    FormatterOptions,
    InspectorOutputJSONEncoder,
)
from ._organization import organize_messages
from ._dandi_inspection import inspect_dandiset, inspect_dandi_file_path, inspect_url
from .checks import *  # These need to be imported to trigger registration with 'available_checks', but are not exposed

default_check_registry = {check.__name__: check for check in available_checks}

# Still keeping the legacy magic version attribute requested by some users
__version__ = importlib.metadata.version(distribution_name="nwbinspector")

# Note: this is not exposed at this outer level, but is used here to trigger the automatic submodule import
# (otherwise someone would have to import nwbinspector.testing explicitly)
from .testing import check_streaming_tests_enabled  # noqa: F401

__all__ = [
    "available_checks",
    "default_check_registry",
    "register_check",
    "Importance",
    "Severity",
    "InspectorMessage",
    "validate_config",
    "load_config",
    "configure_checks",
    "InspectorOutputJSONEncoder",
    "inspect_dandiset",
    "inspect_dandi_file_path",
    "inspect_url",
    "inspect_all",
    "inspect_nwbfile",
    "inspect_nwbfile_object",
    "run_checks",
    "format_messages",
    "print_to_console",
    "save_report",
    "MessageFormatter",
    "FormatterOptions",
    "organize_messages",
    "__version__",
    # Public submodules
    "checks",
    "testing",
    "utils",
]
