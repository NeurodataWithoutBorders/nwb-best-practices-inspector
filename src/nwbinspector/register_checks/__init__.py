import warnings

message = "The 'register_checks' submodule has been deprecated. Please import the helper functions from the top-level package."

warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

# Still keep imports functional with warning for soft deprecation cycle
# TODO: remove after 9/15/2024
from .._types import InspectorMessage, Importance, Severity
from .._registration import register_check, available_checks
