"""Helper functions related to NWB for internal use that rely on external dependencies (i.e., pynwb)."""

from typing import Iterable, Type

from pynwb import NWBFile


def all_of_type(nwbfile: NWBFile, neurodata_type: Type) -> Iterable[object]:
    """Iterate over all objects inside an NWBFile object and return those that match the given neurodata_type."""
    for neurodata_object in nwbfile.objects.values():
        if isinstance(neurodata_object, neurodata_type):
            yield neurodata_object


def get_nwbfile_path_from_internal_object(neurodata_object: object) -> str:
    """Determine the file path on disk for a NWBFile given only an internal object of that file."""
    if isinstance(neurodata_object, NWBFile):
        return neurodata_object.container_source

    return neurodata_object.get_ancestor("NWBFile").container_source  # type: ignore
