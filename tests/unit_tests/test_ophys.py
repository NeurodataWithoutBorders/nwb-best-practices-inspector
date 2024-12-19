from datetime import datetime
from unittest import TestCase
from uuid import uuid4

import numpy as np
from hdmf.common.table import DynamicTable, DynamicTableRegion
from pynwb import NWBFile
from pynwb.device import Device
from pynwb.ophys import (
    ImageSegmentation,
    ImagingPlane,
    OpticalChannel,
    PlaneSegmentation,
    RoiResponseSeries,
    TwoPhotonSeries,
)

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import (
    check_emission_lambda_in_nm,
    check_excitation_lambda_in_nm,
    check_image_series_data_size,  # Technically an ImageSeries check, but test is more convenient here
    check_plane_segmentation_image_mask_shape_against_ref_images,
    check_roi_response_series_dims,
    check_roi_response_series_link_to_plane_segmentation,
)


class TestCheckRoiResponseSeries(TestCase):
    def setUp(self):
        nwbfile = NWBFile(
            session_description="", identifier=str(uuid4()), session_start_time=datetime.now().astimezone()
        )

        device = nwbfile.create_device(
            name="Microscope", description="My two-photon microscope", manufacturer="The best microscope manufacturer"
        )
        optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
        imaging_plane = nwbfile.create_imaging_plane(
            name="ImagingPlane",
            optical_channel=optical_channel,
            imaging_rate=30.0,
            description="a very interesting part of the brain",
            device=device,
            excitation_lambda=600.0,
            indicator="GFP",
            location="V1",
            grid_spacing=[0.01, 0.01],
            grid_spacing_unit="meters",
            origin_coords=[1.0, 2.0, 3.0],
            origin_coords_unit="meters",
        )

        img_seg = ImageSegmentation()

        self.plane_segmentation = img_seg.create_plane_segmentation(
            name="PlaneSegmentation",
            description="output from segmenting my favorite imaging plane",
            imaging_plane=imaging_plane,
        )

        self.ophys_module = nwbfile.create_processing_module(
            name="ophys",
            description="optical physiology processed data",
        )

        self.ophys_module.add(img_seg)

        for _ in range(10):
            image_mask = np.zeros((100, 100))
            self.plane_segmentation.add_roi(image_mask=image_mask)
        self.nwbfile = nwbfile

    def test_check_flipped_dims(self):
        rt_region = self.plane_segmentation.create_roi_table_region(
            region=[0, 1, 2, 3, 4],
            description="the first of two ROIs",
        )

        roi_resp_series = RoiResponseSeries(
            name="RoiResponseSeries",
            data=np.ones((5, 40)),  # 50 samples, 2 ROIs
            rois=rt_region,
            unit="n.a.",
            rate=30.0,
        )

        self.ophys_module.add(roi_resp_series)

        assert check_roi_response_series_dims(roi_resp_series) == InspectorMessage(
            message=(
                "The second dimension of data does not match the length of rois, "
                "but instead the first does. Data is oriented incorrectly and should be transposed."
            ),
            importance=Importance.CRITICAL,
            check_function_name="check_roi_response_series_dims",
            object_type="RoiResponseSeries",
            object_name="RoiResponseSeries",
        )

    def test_check_wrong_dims(self):
        rt_region = self.plane_segmentation.create_roi_table_region(
            region=[0, 1, 2, 3, 4],
            description="the first of two ROIs",
        )

        roi_resp_series = RoiResponseSeries(
            name="RoiResponseSeries",
            data=np.ones((10, 40)),  # 50 samples, 2 ROIs
            rois=rt_region,
            unit="n.a.",
            rate=30.0,
        )

        self.ophys_module.add(roi_resp_series)

        assert check_roi_response_series_dims(roi_resp_series) == InspectorMessage(
            message="The second dimension of data does not match the length of rois. Your " "data may be transposed.",
            importance=Importance.CRITICAL,
            check_function_name="check_roi_response_series_dims",
            object_type="RoiResponseSeries",
            object_name="RoiResponseSeries",
        )

    def test_pass_check_roi_response_series_dims(self):
        rt_region = self.plane_segmentation.create_roi_table_region(
            region=[0, 1, 2, 3, 4],
            description="the first of two ROIs",
        )

        roi_resp_series = RoiResponseSeries(
            name="RoiResponseSeries",
            data=np.ones((40, 5)),  # 50 samples, 2 ROIs
            rois=rt_region,
            unit="n.a.",
            rate=30.0,
        )

        assert check_roi_response_series_dims(roi_resp_series) is None

    def test_check_roi_response_series_link_to_plane_segmentation(self):
        dt = DynamicTable(name="name", description="desc")
        dt.add_column("a", "desc")
        for _ in range(5):
            dt.add_row(a=1)
        dtr = DynamicTableRegion(name="n", description="desc", data=[0, 1, 2, 3, 4], table=dt)
        roi_resp_series = RoiResponseSeries(
            name="RoiResponseSeries",
            data=np.ones((40, 5)),  # 50 samples, 2 ROIs
            rois=dtr,
            unit="n.a.",
            rate=30.0,
        )

        self.ophys_module.add(roi_resp_series)

        assert check_roi_response_series_link_to_plane_segmentation(roi_resp_series) == InspectorMessage(
            message="rois field does not point to a PlaneSegmentation table.",
            importance=Importance.BEST_PRACTICE_VIOLATION,
            check_function_name="check_roi_response_series_link_to_plane_segmentation",
            object_type="RoiResponseSeries",
            object_name="RoiResponseSeries",
        )

    def test_pass_check_roi_response_series_link_to_plane_segmentation(self):
        rt_region = self.plane_segmentation.create_roi_table_region(
            region=[0, 1, 2, 3, 4],
            description="the first of two ROIs",
        )

        roi_resp_series = RoiResponseSeries(
            name="RoiResponseSeries",
            data=np.ones((40, 5)),  # 50 samples, 2 ROIs
            rois=rt_region,
            unit="n.a.",
            rate=30.0,
        )

        assert check_roi_response_series_link_to_plane_segmentation(roi_resp_series) is None


def test_check_excitation_lambda_in_nm():
    device = Device(
        name="Microscope", description="My two-photon microscope", manufacturer="The best microscope manufacturer"
    )
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
    imaging_plane = ImagingPlane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30.0,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=1.0,
        indicator="GFP",
        location="V1",
        grid_spacing=[0.01, 0.01],
        grid_spacing_unit="meters",
        origin_coords=[1.0, 2.0, 3.0],
        origin_coords_unit="meters",
    )

    assert check_excitation_lambda_in_nm(imaging_plane).message == "excitation lambda of 1.0 should be in units of nm."


def test_pass_check_excitation_lambda_in_nm():
    device = Device(
        name="Microscope", description="My two-photon microscope", manufacturer="The best microscope manufacturer"
    )
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
    imaging_plane = ImagingPlane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30.0,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=300.0,
        indicator="GFP",
        location="V1",
        grid_spacing=[0.01, 0.01],
        grid_spacing_unit="meters",
        origin_coords=[1.0, 2.0, 3.0],
        origin_coords_unit="meters",
    )

    assert check_excitation_lambda_in_nm(imaging_plane) is None


def test_check_emission_lambda_in_nm():
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=5.0)
    assert check_emission_lambda_in_nm(optical_channel).message == "emission lambda of 5.0 should be in units of nm."


def test_pass_check_emission_lambda_in_nm():
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
    assert check_emission_lambda_in_nm(optical_channel) is None


def test_pass_check_plane_segmentation_image_mask_dims_against_imageseries():
    device = Device(
        name="Microscope", description="My two-photon microscope", manufacturer="The best microscope manufacturer"
    )
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
    imaging_plane = ImagingPlane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30.0,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=300.0,
        indicator="GFP",
        location="V1",
        grid_spacing=[0.01, 0.01],
        grid_spacing_unit="meters",
        origin_coords=[1.0, 2.0, 3.0],
        origin_coords_unit="meters",
    )

    two_photon_series = TwoPhotonSeries(
        name="TwoPhotonSeries",
        imaging_plane=imaging_plane,
        data=np.ones((20, 10, 10)),
        unit="n.a.",
        rate=30.0,
    )

    plane_segmentation = PlaneSegmentation(
        description="my plane segmentation",
        imaging_plane=imaging_plane,
        reference_images=two_photon_series,
    )

    plane_segmentation.add_roi(image_mask=np.ones((10, 10)))

    assert check_plane_segmentation_image_mask_shape_against_ref_images(plane_segmentation) is None


def test_fail_check_plane_segmentation_image_mask_dims_against_imageseries():
    device = Device(
        name="Microscope", description="My two-photon microscope", manufacturer="The best microscope manufacturer"
    )
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
    imaging_plane = ImagingPlane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30.0,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=300.0,
        indicator="GFP",
        location="V1",
        grid_spacing=[0.01, 0.01],
        grid_spacing_unit="meters",
        origin_coords=[1.0, 2.0, 3.0],
        origin_coords_unit="meters",
    )

    two_photon_series = TwoPhotonSeries(
        name="TwoPhotonSeries",
        imaging_plane=imaging_plane,
        data=np.ones((20, 10, 10)),
        unit="n.a.",
        rate=30.0,
    )

    plane_segmentation = PlaneSegmentation(
        description="my plane segmentation",
        imaging_plane=imaging_plane,
        reference_images=two_photon_series,
    )

    plane_segmentation.add_roi(image_mask=np.ones((9, 10)))

    assert check_plane_segmentation_image_mask_shape_against_ref_images(plane_segmentation) == [
        InspectorMessage(
            message="image_mask of shape (9, 10) does not match reference image TwoPhotonSeries with shape (10, 10).",
            importance=Importance.BEST_PRACTICE_VIOLATION,
            check_function_name="check_plane_segmentation_image_mask_shape_against_ref_images",
            object_type="PlaneSegmentation",
            object_name="ImagingPlane",
            location="/",
        )
    ]


def test_false_positive_skip_check_image_series_data_size():
    device = Device(
        name="Microscope", description="My two-photon microscope", manufacturer="The best microscope manufacturer"
    )
    optical_channel = OpticalChannel(name="OpticalChannel", description="an optical channel", emission_lambda=500.0)
    imaging_plane = ImagingPlane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30.0,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=300.0,
        indicator="GFP",
        location="V1",
        grid_spacing=[0.01, 0.01],
        grid_spacing_unit="meters",
        origin_coords=[1.0, 2.0, 3.0],
        origin_coords_unit="meters",
    )

    two_photon_series = TwoPhotonSeries(
        name="TwoPhotonSeries",
        imaging_plane=imaging_plane,
        data=np.empty(
            shape=(110 * 10**6, 1, 1), dtype="uint8"
        ),  # Empty data, but of shape+dtype that would be more than default GB threshold
        unit="n.a.",
        rate=30.0,
    )

    assert check_image_series_data_size(image_series=two_photon_series, gb_lower_bound=0.1) is None
