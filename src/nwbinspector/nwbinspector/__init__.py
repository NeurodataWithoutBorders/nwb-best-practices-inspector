import warnings

message = (
    "The 'nwbinspector.nwbinspector' submodule has been deprecated. "
    "Please import the helper functions from the top-level package."
)

warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

# Still keep imports functional with warning for soft deprecation cycle
# TODO: remove after 9/15/2024
from .._configuration import (
    INTERNAL_CONFIGS,
    validate_config,
    copy_check,
    load_config,
    configure_checks,
)
from .._nwb_inspection import (
    inspect_all,
    inspect_nwbfile,
    inspect_nwbfile_object,
    run_checks,
)
from .._formatting import InspectorOutputJSONEncoder
