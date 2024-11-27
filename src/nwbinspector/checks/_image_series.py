"""Check functions specific to ImageSeries."""

import ntpath
from pathlib import Path
from typing import Iterable, Optional

from pynwb.image import ImageSeries
from pynwb.ophys import TwoPhotonSeries

from .._registration import Importance, InspectorMessage, register_check
from ..tools import get_nwbfile_path_from_internal_object


@register_check(importance=Importance.CRITICAL, neurodata_type=ImageSeries)
def check_image_series_external_file_valid(image_series: ImageSeries) -> Optional[Iterable[InspectorMessage]]:
    """
    Check if the external_file specified by an ImageSeries actually exists.

    Best Practice: :ref:`best_practice_use_external_mode`
    """
    if image_series.external_file is None:
        return None
    nwbfile_path = Path(get_nwbfile_path_from_internal_object(neurodata_object=image_series))
    for file_path in image_series.external_file:
        file_path = file_path.decode() if isinstance(file_path, bytes) else file_path
        if not Path(file_path).is_absolute() and not (nwbfile_path.parent / file_path).exists():
            yield InspectorMessage(
                message=(
                    f"The external file '{file_path}' does not exist. Please confirm the relative location to the"
                    " NWBFile."
                )
            )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=ImageSeries)
def check_image_series_external_file_relative(image_series: ImageSeries) -> Optional[Iterable[InspectorMessage]]:
    """
    Check if the external_file specified by an ImageSeries, if it exists, is relative.

    Best Practice: :ref:`best_practice_use_external_mode`
    """
    if image_series.external_file is None:
        return None
    for file_path in image_series.external_file:
        file_path = file_path.decode() if isinstance(file_path, bytes) else file_path
        if ntpath.isabs(file_path):  # ntpath required for cross-platform detection
            yield InspectorMessage(
                message=(
                    f"The external file '{file_path}' is not a relative path. "
                    "Please adjust the absolute path to be relative to the location of the NWBFile."
                )
            )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=ImageSeries)
def check_image_series_data_size(image_series: ImageSeries, gb_lower_bound: float = 20.0) -> Optional[InspectorMessage]:
    """
    Check if an ImageSeries stored is larger than gb_lower_bound and suggests external file.

    Best Practice: :ref:`best_practice_use_external_mode`
    """
    # False positive case; TwoPhotonSeries are a subclass of ImageSeries, but it is very common and perfectly fine
    # to write lots of data using one without an external file
    if isinstance(image_series, TwoPhotonSeries):
        return None

    data = image_series.data

    if getattr(data, "compression", None) is not None:
        data_size_gb = data.id.get_storage_size() / 1e9
    else:
        data_size_gb = data.size * data.dtype.itemsize / 1e9

    if data_size_gb > gb_lower_bound:
        return InspectorMessage(message="ImageSeries is very large. Consider using external mode for better storage.")

    return None
