import numpy as np
from pynwb import TimeSeries
from pynwb.base import ImageReferences, Images
from pynwb.image import GrayscaleImage, IndexSeries

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import (
    check_index_series_points_to_image,
    check_order_of_images_len,
    check_order_of_images_unique,
)


def test_check_order_of_images_unique():
    imgs = [GrayscaleImage(name=f"image{i}", data=np.random.randn(10, 10)) for i in range(5)]
    img_refs = ImageReferences(name="order_of_images", data=imgs + [imgs[0]])
    images = Images(name="my_images", images=imgs, order_of_images=img_refs)

    assert check_order_of_images_unique(images) == InspectorMessage(
        message="order_of_images should have unique values.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_order_of_images_unique",
        object_type="Images",
        object_name="my_images",
        location="/",
    )


def test_pass_check_order_of_images_unique():
    imgs = [GrayscaleImage(name=f"image{i}", data=np.random.randn(10, 10)) for i in range(5)]
    img_refs = ImageReferences(name="order_of_images", data=imgs)
    images = Images(name="my_images", images=imgs, order_of_images=img_refs)

    assert check_order_of_images_unique(images) is None


def test_check_order_of_images_len():
    imgs = [GrayscaleImage(name=f"image{i}", data=np.random.randn(10, 10)) for i in range(5)]
    img_refs = ImageReferences(name="order_of_images", data=imgs + [imgs[0]])
    images = Images(name="my_images", images=imgs, order_of_images=img_refs)

    assert check_order_of_images_len(images) == InspectorMessage(
        message="Length of order_of_images (6) does not match the number of images (5).",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_order_of_images_len",
        object_type="Images",
        object_name="my_images",
        location="/",
    )


def test_pass_check_order_of_images_len():
    imgs = [GrayscaleImage(name=f"image{i}", data=np.random.randn(10, 10)) for i in range(5)]
    img_refs = ImageReferences(name="order_of_images", data=imgs)
    images = Images(name="my_images", images=imgs, order_of_images=img_refs)

    assert check_order_of_images_len(images) is None


def test_pass_check_index_series_points_to_image():
    gs_img = GrayscaleImage(
        name="random grayscale",
        data=np.empty(shape=(40, 50), dtype=np.uint8),
        resolution=70.0,
        description="Grayscale version of a raccoon.",
    )

    images = Images(
        name="images",
        images=[gs_img],
        description="An example collection.",
        order_of_images=ImageReferences("order_of_images", [gs_img]),
    )

    idx_series = IndexSeries(
        name="stimuli",
        data=[0, 1, 0, 1],
        indexed_images=images,
        unit="N/A",
        timestamps=[0.1, 0.2, 0.3, 0.4],
    )

    assert check_index_series_points_to_image(idx_series) is None


def test_fail_check_index_series_points_to_image():
    time_series = TimeSeries(
        name="TimeSeries",
        data=np.empty(shape=(2, 50, 40)),
        rate=400.0,
        description="description",
        unit="n.a.",
    )

    idx_series = IndexSeries(
        name="stimuli",
        data=[0, 1, 0, 1],
        indexed_timeseries=time_series,
        unit="N/A",
        timestamps=[0.1, 0.2, 0.3, 0.4],
    )

    assert check_index_series_points_to_image(idx_series) == InspectorMessage(
        object_name="stimuli",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        object_type="IndexSeries",
        message="Pointing an IndexSeries to a TimeSeries will be deprecated. Please point to an Images container "
        "instead.",
        location="/",
        check_function_name="check_index_series_points_to_image",
    )
