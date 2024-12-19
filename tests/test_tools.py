from datetime import datetime
from uuid import uuid4

import numpy as np
import pynwb
from hdmf.testing import TestCase

from nwbinspector import Importance, InspectorMessage, Severity, organize_messages
from nwbinspector.tools import all_of_type


def test_all_of_type():
    nwbfile = pynwb.NWBFile(
        session_description="Testing inspector.",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
    )
    true_time_series = [
        pynwb.TimeSeries(name=f"time_series_{x}", data=np.zeros(shape=(100, 10)), rate=1.0, unit="") for x in range(4)
    ]
    for x in range(2):
        nwbfile.add_acquisition(true_time_series[x])
    ecephys_module = nwbfile.create_processing_module(name="ecephys", description="")
    ecephys_module.add(true_time_series[2])
    ophys_module = nwbfile.create_processing_module(name="ophys", description="")
    ophys_module.add(true_time_series[3])

    nwbfile_time_series = [obj for obj in all_of_type(nwbfile=nwbfile, neurodata_type=pynwb.TimeSeries)]
    for time_series in true_time_series:
        assert time_series in nwbfile_time_series


class TestOrganization(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.messages = [
            InspectorMessage(
                message="test1",
                importance=Importance.BEST_PRACTICE_SUGGESTION,
                check_function_name="fun1",
                object_type="ElectricalSeries",
                object_name="ts1",
                location="/acquisition/",
                file_path="path1/file1.nwb",
            ),
            InspectorMessage(
                message="test2",
                importance=Importance.CRITICAL,
                check_function_name="fun2",
                object_type="DynamicTable",
                object_name="tab",
                location="/acquisition/",
                file_path="path1/file1.nwb",
            ),
            InspectorMessage(
                message="test3",
                importance=Importance.BEST_PRACTICE_SUGGESTION,
                severity=Severity.HIGH,
                check_function_name="fun3",
                object_type="NWBFile",
                object_name="root",
                location="/",
                file_path="path2/file2.nwb",
            ),
            InspectorMessage(
                message="test4",
                importance=Importance.CRITICAL,
                check_function_name="fun2",
                object_type="ElectricalSeries",
                object_name="ts1",
                location="/processing/ecephys/LFP/",
                file_path="path2/path3/file3.nwb",
            ),
        ]

    def test_message_level_assertion(self):
        for level in ["message", "object_name", "severity"]:
            with self.assertRaisesWith(
                exc_type=AssertionError,
                exc_msg=(
                    "You must specify levels to organize by that correspond to attributes of the InspectorMessage "
                    "class, excluding the text message, object_name, and severity."
                ),
            ):
                organize_messages(messages=self.messages, levels=[level])

    def test_file_by_importance(self):
        test_result = organize_messages(messages=self.messages, levels=["file_path", "importance"])
        true_result = {
            "path1/file1.nwb": {
                Importance.CRITICAL: [
                    InspectorMessage(
                        message="test2",
                        importance=Importance.CRITICAL,
                        severity=Severity.LOW,
                        check_function_name="fun2",
                        object_type="DynamicTable",
                        object_name="tab",
                        location="/acquisition/",
                        file_path="path1/file1.nwb",
                    )
                ],
                Importance.BEST_PRACTICE_SUGGESTION: [
                    InspectorMessage(
                        message="test1",
                        importance=Importance.BEST_PRACTICE_SUGGESTION,
                        severity=Severity.LOW,
                        check_function_name="fun1",
                        object_type="ElectricalSeries",
                        object_name="ts1",
                        location="/acquisition/",
                        file_path="path1/file1.nwb",
                    )
                ],
            },
            "path2/file2.nwb": {
                Importance.BEST_PRACTICE_SUGGESTION: [
                    InspectorMessage(
                        message="test3",
                        importance=Importance.BEST_PRACTICE_SUGGESTION,
                        severity=Severity.HIGH,
                        check_function_name="fun3",
                        object_type="NWBFile",
                        object_name="root",
                        location="/",
                        file_path="path2/file2.nwb",
                    )
                ]
            },
            "path2/path3/file3.nwb": {
                Importance.CRITICAL: [
                    InspectorMessage(
                        message="test4",
                        importance=Importance.CRITICAL,
                        severity=Severity.LOW,
                        check_function_name="fun2",
                        object_type="ElectricalSeries",
                        object_name="ts1",
                        location="/processing/ecephys/LFP/",
                        file_path="path2/path3/file3.nwb",
                    )
                ]
            },
        }
        self.assertDictEqual(d1=test_result, d2=true_result)

    def test_reverse(self):
        test_result = organize_messages(
            messages=self.messages, levels=["importance", "file_path"], reverse=[False, True]
        )
        true_result = {
            Importance.CRITICAL: {
                "path2/path3/file3.nwb": [
                    InspectorMessage(
                        message="test4",
                        importance=Importance.CRITICAL,
                        severity=Severity.LOW,
                        check_function_name="fun2",
                        object_type="ElectricalSeries",
                        object_name="ts1",
                        location="/processing/ecephys/LFP/",
                        file_path="path2/path3/file3.nwb",
                    )
                ],
                "path1/file1.nwb": [
                    InspectorMessage(
                        message="test2",
                        importance=Importance.CRITICAL,
                        severity=Severity.LOW,
                        check_function_name="fun2",
                        object_type="DynamicTable",
                        object_name="tab",
                        location="/acquisition/",
                        file_path="path1/file1.nwb",
                    )
                ],
            },
            Importance.BEST_PRACTICE_SUGGESTION: {
                "path2/file2.nwb": [
                    InspectorMessage(
                        message="test3",
                        importance=Importance.BEST_PRACTICE_SUGGESTION,
                        severity=Severity.HIGH,
                        check_function_name="fun3",
                        object_type="NWBFile",
                        object_name="root",
                        location="/",
                        file_path="path2/file2.nwb",
                    )
                ],
                "path1/file1.nwb": [
                    InspectorMessage(
                        message="test1",
                        importance=Importance.BEST_PRACTICE_SUGGESTION,
                        severity=Severity.LOW,
                        check_function_name="fun1",
                        object_type="ElectricalSeries",
                        object_name="ts1",
                        location="/acquisition/",
                        file_path="path1/file1.nwb",
                    )
                ],
            },
        }
        self.assertDictEqual(d1=test_result, d2=true_result)
