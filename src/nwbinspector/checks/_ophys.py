"""Check functions specific to optical electrophysiology neurodata types."""

from typing import Iterable, Optional

from pynwb.ophys import (
    ImagingPlane,
    OpticalChannel,
    PlaneSegmentation,
    RoiResponseSeries,
)

from .._registration import Importance, InspectorMessage, register_check
from ..utils import get_data_shape

MIN_LAMBDA = 10.0  # trigger warnings for wavelength values less than this value


@register_check(importance=Importance.CRITICAL, neurodata_type=RoiResponseSeries)
def check_roi_response_series_dims(roi_response_series: RoiResponseSeries) -> Optional[InspectorMessage]:
    """
    Check the dimensions of an ROI series to ensure the time axis is the correct dimension.

    Best Practice: :ref:`best_practice_data_orientation`
    """
    data = roi_response_series.data
    rois = roi_response_series.rois

    data_shape = get_data_shape(data, strict_no_data_load=True)

    if data_shape and len(data_shape) == 2 and data_shape[1] != len(rois.data):
        if data_shape[0] == len(rois.data):
            return InspectorMessage(
                message=(
                    "The second dimension of data does not match the length of rois, "
                    "but instead the first does. Data is oriented incorrectly and should be transposed."
                )
            )
        return InspectorMessage(
            message="The second dimension of data does not match the length of rois. Your data may be transposed."
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=RoiResponseSeries)
def check_roi_response_series_link_to_plane_segmentation(
    roi_response_series: RoiResponseSeries,
) -> Optional[InspectorMessage]:
    """
    Check that each ROI response series links to a plane segmentation.

    Best Practice: TODO
    """
    if not isinstance(roi_response_series.rois.table, PlaneSegmentation):
        return InspectorMessage(message="rois field does not point to a PlaneSegmentation table.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=OpticalChannel)
def check_emission_lambda_in_nm(optical_channel: OpticalChannel) -> Optional[InspectorMessage]:
    """
    Check that emission lambda is in feasible range for unit nanometers.

    Best Practice: :ref:`best_practice_unit_of_measurement`
    """
    if optical_channel.emission_lambda < MIN_LAMBDA:
        return InspectorMessage(f"emission lambda of {optical_channel.emission_lambda} should be in units of nm.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=ImagingPlane)
def check_excitation_lambda_in_nm(imaging_plane: ImagingPlane) -> Optional[InspectorMessage]:
    """
    Check that emission lambda is in feasible range for unit nanometers.

    Best Practice: :ref:`best_practice_unit_of_measurement`
    """
    if imaging_plane.excitation_lambda < MIN_LAMBDA:
        return InspectorMessage(f"excitation lambda of {imaging_plane.excitation_lambda} should be in units of nm.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=PlaneSegmentation)
def check_plane_segmentation_image_mask_shape_against_ref_images(
    plane_segmentation: PlaneSegmentation,
) -> Optional[Iterable[InspectorMessage]]:
    """Check that image masks and reference images have the same shape."""
    if plane_segmentation.reference_images and "image_mask" in plane_segmentation.colnames:
        mask_shape = plane_segmentation["image_mask"].shape[1:]
        for ref_image in plane_segmentation.reference_images:
            if mask_shape != ref_image.data.shape[1:]:
                yield InspectorMessage(
                    f"image_mask of shape {mask_shape} does not match reference image {ref_image.name} with shape"
                    f" {ref_image.data.shape[1:]}."
                )

    return None
