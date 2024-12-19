from unittest import TestCase

from jsonschema import ValidationError

from nwbinspector import (
    Importance,
    available_checks,
    configure_checks,
    default_check_registry,
    load_config,
    validate_config,
)
from nwbinspector._configuration import _copy_function
from nwbinspector.checks import (
    check_data_orientation,
    check_regular_timestamps,
    check_small_dataset_compression,
    check_timestamps_match_first_dimension,
)


class TestCheckConfiguration(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks = [
            check_small_dataset_compression,
            check_regular_timestamps,
            check_data_orientation,
            check_timestamps_match_first_dimension,
        ]

    def test_safe_check_copy(self):
        initial_importance = available_checks[0].importance
        changed_check = _copy_function(function=available_checks[0])
        if initial_importance is Importance.CRITICAL:
            changed_importance = Importance.BEST_PRACTICE_SUGGESTION
        else:
            changed_importance = Importance.CRITICAL
        changed_check.importance = changed_importance
        assert available_checks[0].importance is initial_importance
        assert changed_check.importance is changed_importance

    def test_configure_checks_change_importance(self):
        config = dict(
            CRITICAL=["check_small_dataset_compression"],
            BEST_PRACTICE_SUGGESTION=["check_regular_timestamps"],
        )
        checks_out = configure_checks(checks=self.checks, config=config)
        assert (
            checks_out[0].__name__ == "check_small_dataset_compression"
            and checks_out[0].importance is Importance.CRITICAL
        )
        assert (
            checks_out[1].__name__ == "check_regular_timestamps"
            and checks_out[1].importance is Importance.BEST_PRACTICE_SUGGESTION
        )

    def test_configure_checks_with_critical_threshold_against_entire_registry(self):
        checks_out = configure_checks(
            checks=available_checks,
            config=load_config(filepath_or_keyword="dandi"),
            importance_threshold=Importance.CRITICAL,
        )
        for check in checks_out:
            assert (
                check.importance is Importance.CRITICAL
            ), f"Check function {check.__name__} with importance {check.importance} is below the set threshold!"

    def test_configure_checks_with_critical_threshold_against_entire_registry_not_include_orientation(self):
        checks_out = configure_checks(
            checks=available_checks,
            config=load_config(filepath_or_keyword="dandi"),
            importance_threshold=Importance.CRITICAL,
        )
        assert len(list(filter(lambda x: x.__name__ == "check_data_orientation", checks_out))) == 0

    def test_configure_checks_no_change(self):
        config = dict(CRITICAL=["check_data_orientation"])
        validate_config(config=config)
        checks_out = configure_checks(checks=self.checks, config=config)
        assert checks_out[2].__name__ == "check_data_orientation", checks_out[2].importance is Importance.CRITICAL

    def test_configure_checks_skip(self):
        config = dict(SKIP=["check_timestamps_match_first_dimension"])
        validate_config(config=config)
        checks_out = configure_checks(checks=self.checks, config=config)
        self.assertListEqual(list1=[x.__name__ for x in checks_out], list2=[x.__name__ for x in self.checks[:3]])

    def test_bad_schema(self):
        config = dict(WRONG="test")
        with self.assertRaises(expected_exception=ValidationError):
            validate_config(config=config)

    def test_load_config(self):
        config = load_config(filepath_or_keyword="dandi")
        self.assertDictEqual(
            d1=config,
            d2=dict(
                CRITICAL=[
                    "check_subject_exists",
                    "check_subject_id_exists",
                    "check_subject_sex",
                    "check_subject_species_exists",
                    "check_subject_species_form",
                    "check_subject_age",
                    "check_subject_proper_age_range",
                ],
                BEST_PRACTICE_VIOLATION=[
                    "check_data_orientation",
                ],
            ),
        )

    def test_all_config_check_names_are_in_default_registry(self):
        config = load_config(filepath_or_keyword="dandi")
        for importance_level, check_names in config.items():
            for check_name in check_names:
                assert (
                    check_name in default_check_registry
                ), f"Check name {check_name} was not found in the default registry!"
