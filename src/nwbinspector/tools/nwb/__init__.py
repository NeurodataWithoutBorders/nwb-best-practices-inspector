import warnings

message = (
    "The submodule 'nwbinspector.tools.nwb' has been deprecated. "
    "Please perform any imports directly from 'nwbinspector.tools' instead."
)

warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

# Still keep imports functional with warning for soft deprecation cycle
# TODO: remove after 9/15/2024
from .._nwb import *
