from hdmf.common import DynamicTable, DynamicTableRegion

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import check_description, check_name_slashes


def test_check_name_slashes_pass():
    table = DynamicTable(name="test_name", description="")
    assert check_name_slashes(neurodata_object=table) is None


def test_check_name_slashes_fail():
    """HDMF/PyNWB forbid "/" in the object names. Might need an external file written in MATLAB to test that?"""
    for x in ["\\"]:
        table = DynamicTable(name=f"test{x}ing", description="")
        assert check_name_slashes(neurodata_object=table) == InspectorMessage(
            message="Object name contains slashes.",
            importance=Importance.CRITICAL,
            check_function_name="check_name_slashes",
            object_type="DynamicTable",
            object_name=f"test{x}ing",
            location="/",
        )


def test_check_description_pass():
    table = DynamicTable(name="test", description="testing")
    assert check_description(neurodata_object=table) is None


def test_check_description_fail():
    table = DynamicTable(name="test", description="No Description.")
    assert check_description(neurodata_object=table) == InspectorMessage(
        message="Description ('No Description.') is a placeholder.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_description",
        object_type="DynamicTable",
        object_name="test",
        location="/",
    )


def test_check_description_missing():
    table = DynamicTable(name="test", description=" ")
    assert check_description(neurodata_object=table) == InspectorMessage(
        message="Description is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_description",
        object_type="DynamicTable",
        object_name="test",
        location="/",
    )


def test_check_description_feature_extraction():
    import numpy as np
    from pynwb.ecephys import FeatureExtraction
    from pynwb.testing.mock.ecephys import mock_ElectrodeTable

    electrodes = mock_ElectrodeTable()

    dynamic_table_region = DynamicTableRegion(
        name="electrodes", description="I am wrong", data=[0, 1, 2, 3, 4], table=electrodes
    )

    feature_extraction = FeatureExtraction(
        name="PCA_features",
        electrodes=dynamic_table_region,
        description=["PC1", "PC2", "PC3", "PC4"],
        times=[0.033, 0.066, 0.099],
        features=np.random.rand(3, 5, 4),  # time, channel, feature
    )

    assert check_description(neurodata_object=feature_extraction) is None
