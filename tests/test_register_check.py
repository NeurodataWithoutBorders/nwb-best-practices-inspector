from enum import Enum

from hdmf.common import DynamicTable
from hdmf.testing import TestCase
from pynwb import TimeSeries

from nwbinspector import Importance, InspectorMessage, Severity, register_check


class TestRegisterClass(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.default_time_series = TimeSeries(name="temp", data=[], unit="", rate=1.0)

    def assertFunctionInChecks(self, check_function, available_checks):
        function_names = [x.__name__ for x in available_checks]
        self.assertIn(member=check_function.__name__, container=function_names)

    def test_register_importance_error_non_enum_type(self):
        bad_importance = "test_bad_importance"

        with self.assertRaisesWith(
            exc_type=ValueError,
            exc_msg=(
                f"Indicated importance ({bad_importance}) of custom check (bad_importance_function) is not a valid "
                "importance level! Please choose one of Importance.CRITICAL, Importance.BEST_PRACTICE_VIOLATION, "
                "or Importance.BEST_PRACTICE_SUGGESTION."
            ),
        ):

            @register_check(importance=bad_importance, neurodata_type=None)
            def bad_importance_function():
                pass

    def test_register_importance_error_enum_type(self):
        class SomeRandomEnum(Enum):
            random_name = -1

        bad_importance = SomeRandomEnum.random_name

        with self.assertRaisesWith(
            exc_type=ValueError,
            exc_msg=(
                f"Indicated importance ({bad_importance}) of custom check (bad_importance_function) is not a valid "
                "importance level! Please choose one of Importance.CRITICAL, Importance.BEST_PRACTICE_VIOLATION, "
                "or Importance.BEST_PRACTICE_SUGGESTION."
            ),
        ):

            @register_check(importance=bad_importance, neurodata_type=None)
            def bad_importance_function():
                pass

    def test_register_importance_error_both_forbidden_check_levels(self):
        for forbidden_importance in [Importance.ERROR, Importance.PYNWB_VALIDATION]:
            with self.assertRaisesWith(
                exc_type=ValueError,
                exc_msg=(
                    f"Indicated importance ({forbidden_importance}) of custom check (forbidden_importance_function) is "
                    "not a valid importance level! Please choose one of Importance.CRITICAL, "
                    "Importance.BEST_PRACTICE_VIOLATION, or Importance.BEST_PRACTICE_SUGGESTION."
                ),
            ):

                @register_check(importance=forbidden_importance, neurodata_type=None)
                def forbidden_importance_function():
                    pass

    def test_register_severity_error(self):
        bad_severity = "test_bad_severity"

        with self.assertRaisesWith(
            exc_type=ValueError,
            exc_msg=(
                f"Indicated severity ({bad_severity}) of custom check "
                "(bad_severity_function) is not a valid severity level! Please choose one of "
                "Severity.HIGH, Severity.LOW, or do not specify any severity."
            ),
        ):

            @register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=None)
            def bad_severity_function(time_series: TimeSeries):
                return InspectorMessage(severity=bad_severity, message="")

            bad_severity_function(time_series=self.default_time_series)

    def test_register_all_severity_levels(self):
        importance = Importance.BEST_PRACTICE_SUGGESTION
        for severity in Severity:

            @register_check(importance=importance, neurodata_type=TimeSeries)
            def good_check_function(time_series: TimeSeries):
                return InspectorMessage(severity=severity, message="")

            self.assertEqual(
                first=good_check_function(time_series=self.default_time_series),
                second=InspectorMessage(
                    severity=severity,
                    message="",
                    importance=importance,
                    check_function_name="good_check_function",
                    object_type="TimeSeries",
                    object_name="temp",
                    location="/",
                ),
            )

    def test_register_missing_severity(self):
        importance = Importance.BEST_PRACTICE_SUGGESTION

        @register_check(importance=importance, neurodata_type=TimeSeries)
        def good_check_function(time_series: TimeSeries):
            return InspectorMessage(message="")

        self.assertEqual(
            first=good_check_function(time_series=self.default_time_series),
            second=InspectorMessage(
                message="",
                importance=importance,
                severity=Severity.LOW,
                check_function_name="good_check_function",
                object_type="TimeSeries",
                object_name="temp",
                location="/",
            ),
        )

    def test_register_available_checks_all_importance_levels_same_neurodata_type(self):
        from nwbinspector import available_checks

        neurodata_type = DynamicTable
        for importance in [
            Importance.CRITICAL,
            Importance.BEST_PRACTICE_VIOLATION,
            Importance.BEST_PRACTICE_SUGGESTION,
        ]:

            @register_check(importance=importance, neurodata_type=neurodata_type)
            def good_check_function():
                pass

            assert good_check_function in available_checks

    def test_register_available_checks_same_importance_level_different_neurodata_types(self):
        from nwbinspector import available_checks

        importance = Importance.BEST_PRACTICE_VIOLATION
        neurodata_type_1 = DynamicTable
        neurodata_type_2 = TimeSeries

        @register_check(importance=importance, neurodata_type=neurodata_type_1)
        def good_check_function_1():
            pass

        assert good_check_function_1 in available_checks

        @register_check(importance=importance, neurodata_type=neurodata_type_2)
        def good_check_function_2():
            pass

        assert good_check_function_2 in available_checks

    def test_register_available_checks_different_importance_levels_different_neurodata_types(self):
        from nwbinspector import available_checks

        importance_1 = Importance.BEST_PRACTICE_SUGGESTION
        importance_2 = Importance.BEST_PRACTICE_VIOLATION
        neurodata_type_1 = DynamicTable
        neurodata_type_2 = TimeSeries

        @register_check(importance=importance_1, neurodata_type=neurodata_type_1)
        def good_check_function_1():
            pass

        assert good_check_function_1 in available_checks

        @register_check(importance=importance_2, neurodata_type=neurodata_type_2)
        def good_check_function_2():
            pass

        assert good_check_function_2 in available_checks
