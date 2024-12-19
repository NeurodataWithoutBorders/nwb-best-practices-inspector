from datetime import datetime, timezone
from uuid import uuid4

from pynwb import NWBFile, ProcessingModule
from pynwb.file import Subject

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import (
    check_doi_publications,
    check_experiment_description,
    check_experimenter_exists,
    check_experimenter_form,
    check_institution,
    check_keywords,
    check_processing_module_name,
    check_session_start_time_future_date,
    check_session_start_time_old_date,
    check_subject_age,
    check_subject_exists,
    check_subject_id_exists,
    check_subject_proper_age_range,
    check_subject_sex,
    check_subject_species_exists,
    check_subject_species_form,
)
from nwbinspector.checks._nwbfile_metadata import PROCESSING_MODULE_CONFIG
from nwbinspector.testing import make_minimal_nwbfile

minimal_nwbfile = make_minimal_nwbfile()


def test_check_session_start_time_old_date_pass():
    assert check_session_start_time_old_date(minimal_nwbfile) is None


def test_check_session_start_time_old_date_fail():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime(1970, 1, 1, 0, 0, 0, 0, timezone.utc),
    )
    assert check_session_start_time_old_date(nwbfile) == InspectorMessage(
        message="The session_start_time (1970-01-01 00:00:00+00:00) may not be set to the true date of the recording.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_session_start_time_old_date",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_session_start_time_future_date_pass():
    nwbfile = NWBFile(session_description="", identifier=str(uuid4()), session_start_time=datetime(2010, 1, 1))
    assert check_session_start_time_future_date(nwbfile) is None


def test_check_session_start_time_future_date_fail():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime(2030, 1, 1, 0, 0, 0, 0, timezone.utc),
    )
    assert check_session_start_time_future_date(nwbfile) == InspectorMessage(
        message="The session_start_time (2030-01-01 00:00:00+00:00) is set to a future date and time.",
        importance=Importance.CRITICAL,
        check_function_name="check_session_start_time_future_date",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_experimenter_exists_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        experimenter=["Last, First"],
    )
    assert check_experimenter_exists(nwbfile) is None


def test_check_experimenter_exists_bytestring_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        experimenter=[b"Last, First"],
    )
    assert check_experimenter_exists(nwbfile) is None


def test_check_experimenter_exists_fail():
    assert check_experimenter_exists(minimal_nwbfile) == InspectorMessage(
        message="Experimenter is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_experimenter_exists",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_experimenter_form_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        experimenter=["Last, First"],
    )
    assert check_experimenter_form(nwbfile=nwbfile) is None


def test_check_experimenter_form_bytestring_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        experimenter=[b"Last, First"],
    )
    assert check_experimenter_form(nwbfile=nwbfile) is None


def test_check_experimenter_form_fail():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        experimenter=["First Middle Last"],
    )
    assert check_experimenter_form(nwbfile=nwbfile) == [
        InspectorMessage(
            message=(
                "The name of experimenter 'First Middle Last' does not match any of the accepted DANDI forms: "
                "'LastName, Firstname', 'LastName, FirstName MiddleInitial.' or 'LastName, FirstName, MiddleName'."
            ),
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_experimenter_form",
            object_type="NWBFile",
            object_name="root",
            location="/",
        )
    ]


def test_check_experiment_description():
    assert check_experiment_description(minimal_nwbfile) == InspectorMessage(
        message="Experiment description is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_experiment_description",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_institution():
    assert check_institution(minimal_nwbfile) == InspectorMessage(
        message="Metadata /general/institution is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_institution",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_keywords_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        keywords=["foo", "bar"],
    )
    assert check_keywords(nwbfile) is None


def test_check_keywords_fail():
    assert check_keywords(minimal_nwbfile) == InspectorMessage(
        message="Metadata /general/keywords is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_keywords",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_doi_publications_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        related_publications=["doi:", "http://dx.doi.org/", "https://doi.org/"],
    )
    assert check_doi_publications(nwbfile) is None


def test_check_doi_publications_bytestring_pass():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        related_publications=[b"doi:", b"http://dx.doi.org/", b"https://doi.org/"],
    )
    assert check_doi_publications(nwbfile) is None


def test_check_doi_publications_fail():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        related_publications=["wrong"],
    )
    assert check_doi_publications(nwbfile) == [
        InspectorMessage(
            message=(
                "Metadata /general/related_publications 'wrong' does not start with 'doi: ###' and is not an external "
                "'doi' link."
            ),
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_doi_publications",
            object_type="NWBFile",
            object_name="root",
            location="/",
        )
    ]


def test_check_doi_publications_multiple_fail():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        related_publications=["wrong1", "wrong2"],
    )
    assert check_doi_publications(nwbfile) == [
        InspectorMessage(
            message=(
                "Metadata /general/related_publications 'wrong1' does not start with 'doi: ###' and is not an external "
                "'doi' link."
            ),
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_doi_publications",
            object_type="NWBFile",
            object_name="root",
            location="/",
        ),
        InspectorMessage(
            message=(
                "Metadata /general/related_publications 'wrong2' does not start with 'doi: ###' and is not an external "
                "'doi' link."
            ),
            importance=Importance.BEST_PRACTICE_SUGGESTION,
            check_function_name="check_doi_publications",
            object_type="NWBFile",
            object_name="root",
            location="/",
        ),
    ]


def test_check_subject_sex():
    nwbfile = NWBFile(session_description="", identifier=str(uuid4()), session_start_time=datetime.now().astimezone())
    nwbfile.subject = Subject(subject_id="001")

    assert check_subject_sex(subject=nwbfile.subject) == InspectorMessage(
        message="Subject.sex is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_sex",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_sex_wrong_value():
    subject = Subject(subject_id="001", sex="Female")

    assert check_subject_sex(subject=subject) == InspectorMessage(
        message="Subject.sex should be one of: 'M' (male), 'F' (female), 'O' (other), or 'U' (unknown).",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_sex",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_sex_caenorhabditis_elegans_default_sex():
    subject = Subject(subject_id="001", species="Caenorhabditis elegans", sex="F")

    assert check_subject_sex(subject=subject) == InspectorMessage(
        message="For C. elegans, Subject.sex should be 'XO' (male) or 'XX' (hermaphrodite).",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_sex",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_sex_c_elegans_default_sex():
    subject = Subject(subject_id="001", species="C. elegans", sex="F")

    assert check_subject_sex(subject=subject) == InspectorMessage(
        message="For C. elegans, Subject.sex should be 'XO' (male) or 'XX' (hermaphrodite).",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_sex",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_sex_c_elegans_xo_sex():
    subject = Subject(subject_id="001", species="C. elegans", sex="XO")

    assert check_subject_sex(subject) is None


def test_check_subject_sex_c_elegans_xx_sex():
    subject = Subject(subject_id="001", species="C. elegans", sex="XX")

    assert check_subject_sex(subject) is None


def test_pass_check_subject_age_with_dob():
    subject = Subject(subject_id="001", sex="F", date_of_birth=datetime.now())
    assert check_subject_age(subject) is None


def test_check_subject_age_missing():
    subject = Subject(subject_id="001")
    assert check_subject_age(subject) == InspectorMessage(
        message="Subject is missing age and date_of_birth. Please specify at least one of these fields.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_age",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_age_iso8601_pass():
    subject = Subject(subject_id="001", age="P1D")
    assert check_subject_age(subject) is None


def test_check_subject_age_iso8601_fail():
    subject = Subject(subject_id="001", age="9 months")
    assert check_subject_age(subject) == InspectorMessage(
        message=(
            "Subject age, '9 months', does not follow ISO 8601 duration format, e.g. 'P2Y' for 2 years "
            "or 'P23W' for 23 weeks. You may also specify a range using a '/' separator, e.g., 'P1D/P3D' for an "
            "age range somewhere from 1 to 3 days. If you cannot specify the upper bound of the range, "
            "you may leave the right side blank, e.g., 'P90Y/' means 90 years old or older."
        ),
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_age",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_age_iso8601_range_pass_1():
    subject = Subject(subject_id="001", age="P1D/P3D")
    assert check_subject_age(subject) is None


def test_check_subject_age_iso8601_range_pass_2():
    subject = Subject(subject_id="001", age="P1D/")
    assert check_subject_age(subject) is None


def test_check_subject_age_iso8601_range_fail_1():
    subject = Subject(subject_id="001", age="9 months/12 months")
    assert check_subject_age(subject) == InspectorMessage(
        message=(
            "Subject age, '9 months/12 months', does not follow ISO 8601 duration format, e.g. 'P2Y' for 2 years "
            "or 'P23W' for 23 weeks. You may also specify a range using a '/' separator, e.g., 'P1D/P3D' for an "
            "age range somewhere from 1 to 3 days. If you cannot specify the upper bound of the range, "
            "you may leave the right side blank, e.g., 'P90Y/' means 90 years old or older."
        ),
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_age",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_age_iso8601_range_fail_2():
    subject = Subject(subject_id="001", age="9 months/")
    assert check_subject_age(subject) == InspectorMessage(
        message=(
            "Subject age, '9 months/', does not follow ISO 8601 duration format, e.g. 'P2Y' for 2 years "
            "or 'P23W' for 23 weeks. You may also specify a range using a '/' separator, e.g., 'P1D/P3D' for an "
            "age range somewhere from 1 to 3 days. If you cannot specify the upper bound of the range, "
            "you may leave the right side blank, e.g., 'P90Y/' means 90 years old or older."
        ),
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_age",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_proper_age_range_pass():
    subject = Subject(subject_id="001", age="P1D/P3D")
    assert check_subject_proper_age_range(subject) is None


def test_check_subject_proper_age_range_fail():
    subject = Subject(subject_id="001", age="P3D/P1D")
    assert check_subject_proper_age_range(subject) == InspectorMessage(
        message=(
            "The durations of the Subject age range, 'P3D/P1D', are not strictly increasing. "
            "The upper (right) bound should be a longer duration than the lower (left) bound."
        ),
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_proper_age_range",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_age_with_years():
    subject = Subject(subject_id="001", age="P1Y/P2Y")
    assert check_subject_age(subject) is None


def test_check_subject_age_with_years_fail():
    subject = Subject(subject_id="001", age="P2Y/P1Y")
    assert check_subject_proper_age_range(subject) == InspectorMessage(
        message=(
            "The durations of the Subject age range, 'P2Y/P1Y', are not strictly increasing. "
            "The upper (right) bound should be a longer duration than the lower (left) bound."
        ),
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_proper_age_range",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_pass_check_subject_species_exists():
    subject = Subject(subject_id="001", species="Homo sapiens")
    assert check_subject_species_exists(subject) is None


def test_check_subject_species_missing():
    subject = Subject(subject_id="001")
    assert check_subject_species_exists(subject) == InspectorMessage(
        message="Subject species is missing.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_subject_species_exists",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def check_subject_species_latin_binomial_pass():
    subject = Subject(subject_id="001", species="Homo sapiens")
    assert check_subject_species_form(subject) is None


def check_subject_species_ncbi_pass():
    subject = Subject(subject_id="001", species="http://purl.obolibrary.org/obo/NCBITaxon_7954")
    assert check_subject_species_form(subject) is None


def test_check_subject_species_not_binomial():
    subject = Subject(subject_id="001", species="Human")

    assert check_subject_species_form(subject) == InspectorMessage(
        message=(
            "Subject species 'Human' should either be in Latin binomial form (e.g., 'Mus musculus' and "
            "'Homo sapiens') or be a NCBI taxonomy link (e.g., 'http://purl.obolibrary.org/obo/NCBITaxon_280675')."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_subject_species_form",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_check_subject_species_c_elegans():
    subject = Subject(subject_id="001", species="C. elegans")

    assert check_subject_species_form(subject) == InspectorMessage(
        message=(
            "Subject species 'C. elegans' should either be in Latin binomial form (e.g., 'Mus musculus' and "
            "'Homo sapiens') or be a NCBI taxonomy link (e.g., 'http://purl.obolibrary.org/obo/NCBITaxon_280675')."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_subject_species_form",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_pass_check_subject_age():
    subject = Subject(subject_id="001", age="P9M")
    assert check_subject_age(subject) is None


def test_check_subject_exists():
    assert check_subject_exists(minimal_nwbfile) == InspectorMessage(
        message="Subject is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_exists",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_pass_check_subject_exists():
    nwbfile = NWBFile(session_description="", identifier=str(uuid4()), session_start_time=datetime.now().astimezone())
    nwbfile.subject = Subject(subject_id="001")
    assert check_subject_exists(nwbfile) is None


def test_check_subject_id_exists():
    subject = Subject(sex="F")
    assert check_subject_id_exists(subject) == InspectorMessage(
        message="subject_id is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_id_exists",
        object_type="Subject",
        object_name="subject",
        location="/general/subject",
    )


def test_pass_check_subject_id_exist():
    subject = Subject(subject_id="001", sex="Male")
    assert check_subject_id_exists(subject) is None


def test_check_processing_module_name():
    processing_module = ProcessingModule("test", "desc")
    assert check_processing_module_name(processing_module) == InspectorMessage(
        message=(
            f"Processing module is named test. It is recommended to use the schema "
            f"module names: {', '.join(PROCESSING_MODULE_CONFIG)}"
        ),
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_processing_module_name",
        object_type="ProcessingModule",
        object_name="test",
        location="/",
    )


def test_pass_check_processing_module_name():
    processing_module = ProcessingModule("ecephys", "desc")
    assert check_processing_module_name(processing_module) is None
