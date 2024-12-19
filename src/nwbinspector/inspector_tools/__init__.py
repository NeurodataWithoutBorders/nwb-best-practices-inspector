import warnings

message = (
    "The 'inspector_tools' submodule has been deprecated. "
    "Please import the helper functions from the top-level package."
)

warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

# Still keep imports functional with warning for soft deprecation cycle
# TODO: remove after 9/15/2024
from .._organization import organize_messages
from .._formatting import (
    format_messages,
    MessageFormatter,
    FormatterOptions,
    print_to_console,
    save_report,
    _get_report_header,
)
