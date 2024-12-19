import warnings

message = (
    "All submodules below the level 'nwbinspector.checks'  have been deprecated. "
    "Please retrieve the specific check function(s) you wish to use from the `available_checks` registry "
    "at the top-level or import directly from 'nwbinspector.checks'."
)

warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

# Still keep imports functional with warning for soft deprecation cycle
# TODO: remove after 9/15/2024
from .._icephys import *
