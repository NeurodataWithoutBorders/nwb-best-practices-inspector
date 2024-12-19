"""Primary decorator used on a check function to add it to the registry and automatically parse its output."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Importance(Enum):
    """A definition of the valid importance levels for a given check function."""

    ERROR = 4
    PYNWB_VALIDATION = 3
    CRITICAL = 2
    BEST_PRACTICE_VIOLATION = 1
    BEST_PRACTICE_SUGGESTION = 0


class Severity(Enum):
    """
    A definition of the valid severity levels for the output from a given check function.

    Strictly for internal development that improves report organization; users should never directly see these values.
    """

    HIGH = 2
    LOW = 1


@dataclass
class InspectorMessage:
    """
    The primary output to be returned by every check function.

    Parameters
    ----------
    message : str
        A message that informs the user of the violation.
    severity : Severity, optional
        If a check of non-CRITICAL importance has some basis of comparison, such as magnitude of affected data, then
        the developer of the check may set the severity as Severity.HIGH or Severity.LOW by calling
        `from nwbinspector.register_checks import Severity`. A good example is comparing if h5py.Dataset compression
        has been enabled on smaller vs. larger objects (see nwbinspector/checks/nwb_containers.py for details).

        The user will never directly see this severity, but it will prioritize the order in which check results are
        presented by the NWBInspector.

    importance : Importance
        The Importance level specified by the decorator of the check function.
    check_function_name : str
        The name of the check function the decorator was applied to.
    object_type : str
        The specific class of the instantiated object being inspected.
    object_name : str
        The name of the instantiated object being inspected.
    location : str
        The location relative to the root of the NWBFile where the inspected object may be found.
    file_path : str
        The path of the NWBFile this message pertains to
        Relative to the path called from inspect_nwb, inspect_all, or the path specified at the command line.
    """

    message: str
    importance: Importance = Importance.BEST_PRACTICE_SUGGESTION
    severity: Severity = Severity.LOW
    check_function_name: Optional[str] = None
    object_type: Optional[str] = None
    object_name: Optional[str] = None
    location: Optional[str] = None
    file_path: Optional[str] = None

    def __repr__(self):
        """Representation for InspectorMessage objects according to black format."""
        return "InspectorMessage(\n" + ",\n".join([f"    {k}={v.__repr__()}" for k, v in self.__dict__.items()]) + "\n)"
