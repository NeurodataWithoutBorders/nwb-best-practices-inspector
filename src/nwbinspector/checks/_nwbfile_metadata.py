"""Check functions that examine general NWBFile metadata."""

import re
from datetime import datetime
from typing import Iterable, Optional

from isodate import Duration, parse_duration
from pynwb import NWBFile, ProcessingModule
from pynwb.file import Subject

from .._registration import Importance, InspectorMessage, register_check
from ..utils import is_module_installed

duration_regex = (
    r"^P(?!$)(\d+(?:\.\d+)?Y)?(\d+(?:\.\d+)?M)?(\d+(?:\.\d+)?W)?(\d+(?:\.\d+)?D)?(T(?=\d)(\d+(?:\.\d+)?H)?(\d+(?:\.\d+)"
    r"?M)?(\d+(?:\.\d+)?S)?)?$"
)
species_form_regex = r"([A-Z][a-z]* [a-z]+)|(http://purl.obolibrary.org/obo/NCBITaxon_\d+)"

PROCESSING_MODULE_CONFIG = ["ophys", "ecephys", "icephys", "behavior", "misc", "ogen", "retinotopy"]


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_session_start_time_old_date(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """
    Check if the session_start_time was set to an appropriate value.

    Best Practice: :ref:`best_practice_global_time_reference`
    """
    session_start_time = nwbfile.session_start_time
    dummy_time = datetime(1980, 1, 1)

    tzinfo = session_start_time.tzinfo
    if tzinfo is not None:
        dummy_time = dummy_time.astimezone(tzinfo)

    if session_start_time <= dummy_time:
        return InspectorMessage(
            message=(f"The session_start_time ({session_start_time}) may not be set to the true date of the recording.")
        )

    return None


@register_check(importance=Importance.CRITICAL, neurodata_type=NWBFile)
def check_session_start_time_future_date(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """
    Check if the session_start_time was set to an appropriate value.

    Best Practice: :ref:`best_practice_global_time_reference`
    """
    session_start_time = nwbfile.session_start_time
    current_time = datetime.now()
    tzinfo = session_start_time.tzinfo
    if session_start_time.tzinfo is not None:
        current_time = current_time.astimezone(tzinfo)

    if session_start_time >= current_time:
        return InspectorMessage(
            message=f"The session_start_time ({session_start_time}) is set to a future date and time."
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_experimenter_exists(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """
    Check if an experimenter has been added for the session.

    Best Practice: :ref:`best_practice_experimenter`
    """
    if not nwbfile.experimenter:
        return InspectorMessage(message="Experimenter is missing.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_experimenter_form(nwbfile: NWBFile) -> Optional[Iterable[InspectorMessage]]:
    """
    Check the text form of each experimenter to see if it matches the DANDI regex pattern.

    Best Practice: :ref:`best_practice_experimenter`
    """
    if nwbfile.experimenter is None:
        return None
    if is_module_installed(module_name="dandi"):
        from dandischema.models import (
            NAME_PATTERN,  # for most up to date version of the regex
        )
    else:
        NAME_PATTERN = r"^([\w\s\-\.']+),\s+([\w\s\-\.']+)$"  # copied on 7/12/22

    for experimenter in nwbfile.experimenter:
        experimenter = experimenter.decode() if isinstance(experimenter, bytes) else experimenter
        if re.match(string=experimenter, pattern=NAME_PATTERN) is None:
            yield InspectorMessage(
                message=(
                    f"The name of experimenter '{experimenter}' does not match any of the accepted DANDI forms: "
                    "'LastName, Firstname', 'LastName, FirstName MiddleInitial.' or 'LastName, FirstName, MiddleName'."
                )
            )

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_experiment_description(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """Check if a description has been added for the session."""
    if not nwbfile.experiment_description:
        return InspectorMessage(message="Experiment description is missing.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_institution(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """Check if a description has been added for the session."""
    if not nwbfile.institution:
        return InspectorMessage(message="Metadata /general/institution is missing.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_keywords(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """Check if keywords have been added for the session."""
    if not nwbfile.keywords:
        return InspectorMessage(message="Metadata /general/keywords is missing.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_subject_exists(nwbfile: NWBFile) -> Optional[InspectorMessage]:
    """Check if subject exists."""
    if nwbfile.subject is None:
        return InspectorMessage(message="Subject is missing.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=NWBFile)
def check_doi_publications(nwbfile: NWBFile) -> Optional[Iterable[InspectorMessage]]:
    """Check if related_publications has been properly added as 'doi: ###' or an external 'doi' link."""
    valid_starts = ["doi:", "http://dx.doi.org/", "https://doi.org/"]

    if not nwbfile.related_publications:
        return None
    for publication in nwbfile.related_publications:
        publication = publication.decode() if isinstance(publication, bytes) else publication
        if not any((publication.startswith(valid_start) for valid_start in valid_starts)):
            yield InspectorMessage(
                message=(
                    f"Metadata /general/related_publications '{publication}' does not start with 'doi: ###' and is "
                    "not an external 'doi' link."
                )
            )

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=Subject)
def check_subject_age(subject: Subject) -> Optional[InspectorMessage]:
    """Check if the Subject age is in ISO 8601 or our extension of it for ranges."""
    if subject.age is None and subject.date_of_birth is None:
        return InspectorMessage(
            message="Subject is missing age and date_of_birth. Please specify at least one of these fields."
        )
    elif subject.age is None and subject.date_of_birth is not None:
        return None
    if re.fullmatch(pattern=duration_regex, string=subject.age):
        return None

    if "/" in subject.age:
        subject_lower_age_bound, subject_upper_age_bound = subject.age.split("/")

        if re.fullmatch(pattern=duration_regex, string=subject_lower_age_bound) and (
            re.fullmatch(pattern=duration_regex, string=subject_upper_age_bound) or subject_upper_age_bound == ""
        ):
            return None

    return InspectorMessage(
        message=(
            f"Subject age, '{subject.age}', does not follow ISO 8601 duration format, e.g. 'P2Y' for 2 years "
            "or 'P23W' for 23 weeks. You may also specify a range using a '/' separator, e.g., 'P1D/P3D' for an "
            "age range somewhere from 1 to 3 days. If you cannot specify the upper bound of the range, "
            "you may leave the right side blank, e.g., 'P90Y/' means 90 years old or older."
        )
    )


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=Subject)
def check_subject_proper_age_range(subject: Subject) -> Optional[InspectorMessage]:
    """
    Check if the Subject age, if specified as duration range (e.g., 'P1D/P3D'), has properly increasing bounds.

    Best Practice: :ref:`best_practice_subject_age`
    """
    if subject.age is not None and "/" in subject.age:
        subject_lower_age_bound, subject_upper_age_bound = subject.age.split("/")

        if re.fullmatch(pattern=duration_regex, string=subject_lower_age_bound) and re.fullmatch(
            pattern=duration_regex, string=subject_upper_age_bound
        ):
            lower = parse_duration(subject_lower_age_bound)
            if isinstance(lower, Duration):
                lower = lower.totimedelta(end=datetime.now())

            upper = parse_duration(subject_upper_age_bound)
            if isinstance(upper, Duration):
                upper = upper.totimedelta(end=datetime.now())

            if lower >= upper:
                return InspectorMessage(
                    message=(
                        f"The durations of the Subject age range, '{subject.age}', are not strictly increasing. "
                        "The upper (right) bound should be a longer duration than the lower (left) bound."
                    )
                )

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=Subject)
def check_subject_id_exists(subject: Subject) -> Optional[InspectorMessage]:
    """Check if subject_id is defined."""
    if subject.subject_id is None:
        return InspectorMessage(message="subject_id is missing.")

    return None


def _check_subject_sex_defaults(sex: str) -> Optional[InspectorMessage]:
    """Check if the subject sex has been specified properly for the C. elegans species."""
    if sex not in ("M", "F", "O", "U"):
        return InspectorMessage(
            message="Subject.sex should be one of: 'M' (male), 'F' (female), 'O' (other), or 'U' (unknown)."
        )

    return None


def _check_subject_sex_c_elegans(sex: str) -> Optional[InspectorMessage]:
    """Check if the subject sex has been specified properly for the C. elegans species."""
    if sex not in ("XO", "XX"):
        return InspectorMessage(message="For C. elegans, Subject.sex should be 'XO' (male) or 'XX' (hermaphrodite).")

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=Subject)
def check_subject_sex(subject: Subject) -> Optional[InspectorMessage]:
    """
    Check if the subject sex has been specified and ensure that it has has the correct form depending on the species.

    Best Practice: :ref:`best_practice_subject_sex`
    """
    if subject and not subject.sex:
        return InspectorMessage(message="Subject.sex is missing.")
    if subject.species in ("Caenorhabditis elegans", "C. elegans"):
        return _check_subject_sex_c_elegans(sex=subject.sex)
    else:
        return _check_subject_sex_defaults(sex=subject.sex)

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=Subject)
def check_subject_species_exists(subject: Subject) -> Optional[InspectorMessage]:
    """
    Check if the subject species has been specified.

    Best Practice: :ref:`best_practice_subject_species`
    """
    if not subject.species:
        return InspectorMessage(message="Subject species is missing.")

    return None


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=Subject)
def check_subject_species_form(subject: Subject) -> Optional[InspectorMessage]:
    """
    Check if the subject species follows latin binomial form or is a link to an NCBI taxonomy in the form of a Term IRI.

    The Term IRI can be found at the https://ontobee.org/ database.

    Best Practice: :ref:`best_practice_subject_species`
    """
    if subject.species and not re.fullmatch(species_form_regex, subject.species):
        return InspectorMessage(
            message=(
                f"Subject species '{subject.species}' should either be in Latin binomial form (e.g., 'Mus musculus' and "
                "'Homo sapiens') or be a NCBI taxonomy link (e.g., 'http://purl.obolibrary.org/obo/NCBITaxon_280675')."
            ),
        )

    return None


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=ProcessingModule)
def check_processing_module_name(processing_module: ProcessingModule) -> Optional[InspectorMessage]:
    """Check if the name of a processing module is of a valid modality."""
    if processing_module.name not in PROCESSING_MODULE_CONFIG:
        return InspectorMessage(
            message=(
                f"Processing module is named {processing_module.name}. It is recommended to use the "
                f"schema module names: {', '.join(PROCESSING_MODULE_CONFIG)}"
            )
        )

    return None
