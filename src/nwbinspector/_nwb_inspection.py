"""Primary functions for inspecting NWBFiles."""

import importlib
import traceback
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Optional, Type, Union
from warnings import filterwarnings, warn

import pynwb
from hdmf_zarr import ZarrIO
from natsort import natsorted
from tqdm import tqdm

from ._configuration import configure_checks
from ._registration import Importance, InspectorMessage, available_checks
from .tools._read_nwbfile import read_nwbfile
from .utils import (
    OptionalListOfStrings,
    PathType,
    calculate_number_of_cpu,
)


def inspect_all(
    path: PathType,
    config: Optional[dict] = None,
    ignore: OptionalListOfStrings = None,
    select: OptionalListOfStrings = None,
    importance_threshold: Union[str, Importance] = Importance.BEST_PRACTICE_SUGGESTION,
    n_jobs: int = 1,
    skip_validate: bool = False,
    progress_bar: bool = True,
    progress_bar_class: Type[tqdm] = tqdm,
    progress_bar_options: Optional[dict] = None,
    stream: bool = False,  # TODO: remove after 3/1/2025
    version_id: Optional[str] = None,  # TODO: remove after 3/1/2025
    modules: OptionalListOfStrings = None,
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Inspect a local NWBFile or folder of NWBFiles and return suggestions for improvements according to best practices.

    Parameters
    ----------
    path : PathType
        File path to an NWBFile, folder path to iterate over recursively and scan all NWBFiles present, or a
        six-digit identifier of the DANDISet.
    config : dict, optional
        If a dictionary, it must be valid against our JSON configuration schema.
        Can specify a mapping of importance levels and list of check functions whose importance you wish to change.
        Typically loaded via json.load from a valid .json file
    ignore: list of strings, optional
        Names of functions to skip.
    select: list of strings, optional
        Names of functions to pick out of available checks.
    importance_threshold : string or Importance, optional
        Ignores tests with an assigned importance below this threshold.
        Importance has three levels:

            CRITICAL
                - potentially incorrect data
            BEST_PRACTICE_VIOLATION
                - very suboptimal data representation
            BEST_PRACTICE_SUGGESTION
                - improvable data representation

        The default is the lowest level, BEST_PRACTICE_SUGGESTION.
    n_jobs : int
        Number of jobs to use in parallel. Set to -1 to use all available resources.
        This may also be a negative integer x from -2 to -(number_of_cpus - 1) which acts like negative slicing by using
        all available CPUs minus x.
        Set to 1 (also the default) to disable.
    skip_validate : bool, optional
        Skip the PyNWB validation step.
        The default is False, which is recommended.
    progress_bar : bool, optional
        Display a progress bar while scanning NWBFiles.
        Defaults to True.
    progress_bar_class : type of tqdm.tqdm, optional
        The specific child class of tqdm.tqdm to use to make progress bars.
        Defaults to tqdm.tqdm, the most generic parent.
    progress_bar_options : dict, optional
        Dictionary of keyword arguments to pass directly to the progress_bar_class.
    modules : list of strings, optional
        List of external module names to load; examples would be namespace extensions.
        These modules may also contain their own custom checks for their extensions.
    """
    in_path = Path(path)
    importance_threshold = (
        Importance[importance_threshold] if isinstance(importance_threshold, str) else importance_threshold
    )
    modules = modules or []

    for module in modules:
        importlib.import_module(module)

    # TODO: remove these blocks after 3/1/2025
    if version_id is not None:
        deprecation_message = (
            "The `version_id` argument is deprecated and will be removed after 3/1/2025. "
            "Please call `nwbinspector.inspect_dandiset` with the argument `dandiset_version` instead."
        )
        warn(message=deprecation_message, category=DeprecationWarning, stacklevel=2)
    if stream:
        from ._dandi_inspection import inspect_dandiset

        warning_message = (
            "The `stream` argument is deprecated and will be removed after 3/1/2025. "
            "Please call `nwbinspector.inspect_dandiset` instead."
        )
        warn(message=warning_message, category=DeprecationWarning, stacklevel=2)

        for message in inspect_dandiset(
            dandiset_id=str(path),
            dandiset_version=version_id,
            config=config,
            ignore=ignore,
            select=select,
            skip_validate=skip_validate,
        ):
            yield message

        return None

    calculated_number_of_jobs = calculate_number_of_cpu(requested_cpu=n_jobs)
    if progress_bar_options is None:
        progress_bar_options = dict(position=0, leave=False)

    if in_path.is_dir() and (in_path.match("*.nwb*")) and ZarrIO.can_read(in_path):
        nwbfiles = [in_path]  # if it is a zarr directory
    elif in_path.is_dir():
        nwbfiles = list(in_path.rglob("*.nwb*"))

        # Remove any macOS sidecar files
        nwbfiles = [nwbfile for nwbfile in nwbfiles if not nwbfile.name.startswith("._")]
    elif in_path.is_file():
        nwbfiles = [in_path]
    else:
        raise ValueError(f"{in_path} should be a directory or an NWB file.")
    # Filtering of checks should apply after external modules are imported, in case those modules have their own checks
    checks = configure_checks(config=config, ignore=ignore, select=select, importance_threshold=importance_threshold)

    # Manual identifier check over all files in the folder path
    identifiers = defaultdict(list)
    for nwbfile_path in nwbfiles:
        try:
            nwbfile = read_nwbfile(nwbfile_path=nwbfile_path)
            identifiers[nwbfile.identifier].append(nwbfile_path)
        except Exception as exception:
            yield InspectorMessage(
                message=traceback.format_exc(),
                importance=Importance.ERROR,
                check_function_name=f"During io.read() - {type(exception)}: {str(exception)}",
                file_path=str(nwbfile_path),
            )

    if len(identifiers) != len(nwbfiles):
        for identifier, nwbfiles_with_identifier in identifiers.items():
            if len(nwbfiles_with_identifier) > 1:
                yield InspectorMessage(
                    message=(
                        f"The identifier '{identifier}' is used across the .nwb files: "
                        f"{natsorted([x.name for x in nwbfiles_with_identifier])}. "
                        "The identifier of any NWBFile should be a completely unique value - "
                        "we recommend using uuid4 to achieve this."
                    ),
                    importance=Importance.CRITICAL,
                    check_function_name="check_unique_identifiers",
                    object_type="NWBFile",
                    object_name="root",
                    location="/",
                    file_path=str(path),
                )

    nwbfiles_iterable = nwbfiles
    if progress_bar:
        nwbfiles_iterable = progress_bar_class(nwbfiles_iterable, **progress_bar_options)
    if calculated_number_of_jobs == 1:
        for nwbfile_path in nwbfiles_iterable:  # type: ignore
            for message in inspect_nwbfile(nwbfile_path=nwbfile_path, checks=checks, skip_validate=skip_validate):
                yield message
    else:
        progress_bar_options.update(total=len(nwbfiles))
        futures = []
        # concurrents uses None instead of -1 for 'auto' mode
        max_workers = None if calculated_number_of_jobs == -1 else calculated_number_of_jobs
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for nwbfile_path in nwbfiles:
                futures.append(
                    executor.submit(
                        _pickle_inspect_nwb,
                        nwbfile_path=str(nwbfile_path),
                        checks=checks,
                        skip_validate=skip_validate,
                    )
                )
            async_nwbfiles_iterable = as_completed(futures)
            if progress_bar:
                async_nwbfiles_iterable = progress_bar_class(async_nwbfiles_iterable, **progress_bar_options)
            for future in async_nwbfiles_iterable:
                for message in future.result():
                    if stream:
                        message.file_path = nwbfiles[message.file_path]
                    yield message


def _pickle_inspect_nwb(
    nwbfile_path: str,
    checks: Optional[list] = None,
    skip_validate: bool = False,
) -> Iterable[Union[InspectorMessage, None]]:
    """Auxiliary function for inspect_all to run in parallel using the ProcessPoolExecutor."""
    checks = checks or available_checks

    return list(inspect_nwbfile(nwbfile_path=nwbfile_path, checks=checks, skip_validate=skip_validate))


def inspect_nwbfile(
    nwbfile_path: Union[str, Path],
    driver: Optional[str] = None,  # TODO: remove after 3/1/2025
    skip_validate: bool = False,
    max_retries: Optional[int] = None,  # TODO: remove after 3/1/2025
    checks: Optional[list] = None,
    config: Optional[dict] = None,
    ignore: OptionalListOfStrings = None,
    select: OptionalListOfStrings = None,
    importance_threshold: Union[str, Importance] = Importance.BEST_PRACTICE_SUGGESTION,
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Open an NWB file, inspect the contents, and return suggestions for improvements according to best practices.

    Parameters
    ----------
    nwbfile_path : FilePathType
        Path to the NWB file on disk or on S3.
    skip_validate : bool
        Skip the PyNWB validation step.
        The default is False, which is recommended.
    checks : list, optional
        List of checks to run.
    config : dict
        Dictionary valid against our JSON configuration schema.
        Can specify a mapping of importance levels and list of check functions whose importance you wish to change.
        Typically loaded via `json.load` from a valid .json file.
    ignore: list, optional
        Names of functions to skip.
    select: list, optional
        Names of functions to pick out of available checks.
    importance_threshold : string or Importance, optional
        Ignores tests with an assigned importance below this threshold.
        Importance has three levels:

            CRITICAL
                - potentially incorrect data
            BEST_PRACTICE_VIOLATION
                - very suboptimal data representation
            BEST_PRACTICE_SUGGESTION
                - improvable data representation

        The default is the lowest level, BEST_PRACTICE_SUGGESTION.
    """
    checks = checks or available_checks
    # TODO: remove error after 3/1/2025
    if driver is not None or max_retries is not None:
        message = (
            "The `driver` and `max_retries` arguments are deprecated and will be removed after 3/1/2025. "
            "Please call `nwbinspector.inspect_dandi_file_path` instead."
        )
        raise ValueError(message)

    nwbfile_path = str(nwbfile_path)
    filterwarnings(action="ignore", message="No cached namespaces found in .*")
    filterwarnings(action="ignore", message="Ignoring cached namespace .*")

    try:
        in_memory_nwbfile = read_nwbfile(nwbfile_path=nwbfile_path)

        if not skip_validate:
            validation_errors, _ = pynwb.validate(paths=[nwbfile_path])
            for validation_error in validation_errors:
                yield InspectorMessage(
                    message=validation_error.reason,
                    importance=Importance.PYNWB_VALIDATION,
                    check_function_name=validation_error.name,
                    location=validation_error.location,
                    file_path=nwbfile_path,
                )

        for inspector_message in inspect_nwbfile_object(
            nwbfile_object=in_memory_nwbfile,
            checks=checks,
            config=config,
            ignore=ignore,
            select=select,
            importance_threshold=importance_threshold,
        ):
            inspector_message.file_path = nwbfile_path  # type: ignore
            yield inspector_message
    except Exception as exception:
        yield InspectorMessage(
            message=traceback.format_exc(),
            importance=Importance.ERROR,
            check_function_name=f"During io.read() - {type(exception)}: {str(exception)}",
            file_path=nwbfile_path,
        )


# TODO: deprecate once subject types and dandi schemas have been extended
def _intercept_in_vitro_protein(nwbfile_object: pynwb.NWBFile, checks: Optional[list] = None) -> list:
    """
    If the special 'protein' subject_id is specified, return a truncated list of checks to run.

    This is a temporary method for allowing upload of certain in vitro data to DANDI and
    is expected to be replaced in future versions.
    """
    checks = checks or available_checks

    subject_related_check_names = [
        "check_subject_exists",
        "check_subject_id_exists",
        "check_subject_sex",
        "check_subject_species_exists",
        "check_subject_species_form",
        "check_subject_age",
        "check_subject_proper_age_range",
    ]
    subject_related_dandi_requirements = [
        check.importance == Importance.CRITICAL  # type: ignore
        for check in checks
        if check.__name__ in subject_related_check_names
    ]

    subject = getattr(nwbfile_object, "subject", None)
    if (
        any(subject_related_dandi_requirements)
        and subject is not None
        and (getattr(subject, "subject_id") or "").startswith("protein")
    ):
        non_subject_checks = [check for check in checks if check.__name__ not in subject_related_check_names]
        return non_subject_checks

    return checks


def inspect_nwbfile_object(
    nwbfile_object: pynwb.NWBFile,
    checks: Optional[list] = None,
    config: Optional[dict] = None,
    ignore: Optional[list[str]] = None,
    select: Optional[list[str]] = None,
    importance_threshold: Union[str, Importance] = Importance.BEST_PRACTICE_SUGGESTION,
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Inspect an in-memory NWBFile object and return suggestions for improvements according to best practices.

    Parameters
    ----------
    nwbfile_object : NWBFile
        An in-memory NWBFile object.
    checks : list, optional
        list of checks to run
    config : dict, optional
        Dictionary valid against our JSON configuration schema.
        Can specify a mapping of importance levels and list of check functions whose importance you wish to change.
        Typically loaded via json.load from a valid .json file
    ignore: list, optional
        Names of functions to skip.
    select: list, optional
        Names of functions to pick out of available checks.
    importance_threshold : string or Importance, optional
        Ignores tests with an assigned importance below this threshold.
        Importance has three levels:

            CRITICAL
                - potentially incorrect data
            BEST_PRACTICE_VIOLATION
                - very suboptimal data representation
            BEST_PRACTICE_SUGGESTION
                - improvable data representation

        The default is the lowest level, BEST_PRACTICE_SUGGESTION.
    """
    checks = checks or available_checks
    importance_threshold = (
        Importance[importance_threshold] if isinstance(importance_threshold, str) else importance_threshold
    )
    if any(argument is not None for argument in [config, ignore, select, importance_threshold]):
        checks = configure_checks(
            checks=checks, config=config, ignore=ignore, select=select, importance_threshold=importance_threshold
        )

    subject_dependent_checks = _intercept_in_vitro_protein(nwbfile_object=nwbfile_object, checks=checks)

    for inspector_message in run_checks(nwbfile=nwbfile_object, checks=subject_dependent_checks):
        yield inspector_message


def run_checks(
    nwbfile: pynwb.NWBFile,
    checks: list,
    progress_bar_class: Optional[Type[tqdm]] = None,
    progress_bar_options: Optional[dict] = None,
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Run checks on an open NWBFile object.

    Parameters
    ----------
    nwbfile : pynwb.NWBFile
        The in-memory pynwb.NWBFile object to run the checks on.
    checks : list of check functions
        The list of check functions that will be run on the in-memory pynwb.NWBFile object.
    progress_bar_class : type of tqdm.tqdm, optional
        The specific child class of tqdm.tqdm to use to make progress bars.
        Defaults to not displaying progress per set of checks over an individual file.
    progress_bar_options : dict, optional
        Dictionary of keyword arguments to pass directly to the `progress_bar_class`.

    Yields
    ------
    results : a generator of InspectorMessage objects
        A generator that returns a message on each iteration, if any are triggered by downstream conditions.
        Otherwise, has length zero (if cast as `list`), or raises `StopIteration` (if explicitly calling `next`).
    """
    if progress_bar_class is not None:
        check_progress = progress_bar_class(iterable=checks, total=len(checks), **progress_bar_options)
    else:
        check_progress = checks

    for check_function in check_progress:
        for nwbfile_object in nwbfile.objects.values():
            if check_function.neurodata_type is not None and not issubclass(
                type(nwbfile_object), check_function.neurodata_type
            ):
                continue

            try:
                output = check_function(nwbfile_object)
            # if an individual check fails, include it in the report and continue with the inspection
            except Exception as exception:
                check_function_name = (
                    f"During evaluation of '{check_function.__name__}' - {type(exception)}: {str(exception)}"
                )
                output = InspectorMessage(
                    message=traceback.format_exc(),
                    importance=Importance.ERROR,
                    check_function_name=check_function_name,
                    file_path="unknown",
                )
            if isinstance(output, InspectorMessage):
                # temporary solution to https://github.com/dandi/dandi-cli/issues/1031
                if output.importance != Importance.ERROR:
                    output.importance = check_function.importance
                yield output
            elif output is not None:
                for x in output:
                    x.importance = check_function.importance
                    yield x
