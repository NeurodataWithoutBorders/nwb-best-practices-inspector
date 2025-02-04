from hdmf.common import DynamicTable, DynamicTableRegion

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import check_description, check_name_colons, check_name_slashes


def test_check_name_slashes_pass():
    table = DynamicTable(name="test_name", description="")
    assert check_name_slashes(neurodata_object=table) is None


def test_check_name_slashes_fail():
    # the latest version of HDMF/PyNWB forbids "/" in the object names when creating a new object
    # so we use in_construct_mode=True to simulate an object that was read from a file
    table = DynamicTable.__new__(DynamicTable, in_construct_mode=True)
    table.__init__(name="test/ing", description="")
    assert check_name_slashes(neurodata_object=table) == InspectorMessage(
        message="Object name contains slashes.",
        importance=Importance.CRITICAL,
        check_function_name="check_name_slashes",
        object_type="DynamicTable",
        object_name="test/ing",
        location="/",
    )

    table = DynamicTable(name="test\\ing", description="")
    assert check_name_slashes(neurodata_object=table) == InspectorMessage(
        message="Object name contains slashes.",
        importance=Importance.CRITICAL,
        check_function_name="check_name_slashes",
        object_type="DynamicTable",
        object_name="test\\ing",
        location="/",
    )


def test_check_name_colons_pass():
    table = DynamicTable(name="test_name", description="")
    assert check_name_colons(neurodata_object=table) is None


def test_check_name_colons_fail():
    # the latest version of HDMF/PyNWB forbids ":" in the object names when creating a new object
    # so we use in_construct_mode=True to simulate an object that was read from a file
    table = DynamicTable.__new__(DynamicTable, in_construct_mode=True)
    table.__init__(name="test:ing", description="")
    assert check_name_colons(neurodata_object=table) == InspectorMessage(
        message="Object name contains colons.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_name_colons",
        object_type="DynamicTable",
        object_name="test:ing",
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
