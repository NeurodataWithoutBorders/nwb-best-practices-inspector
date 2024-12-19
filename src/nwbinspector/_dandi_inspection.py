import pathlib
from typing import Iterable, Literal, Union
from warnings import filterwarnings

import h5py
import pynwb

from ._configuration import load_config, validate_config
from ._nwb_inspection import inspect_nwbfile_object
from ._types import Importance, InspectorMessage


def inspect_dandiset(
    *,
    dandiset_id: str,
    dandiset_version: Union[str, Literal["draft"], None] = None,
    config: Union[str, pathlib.Path, dict, Literal["dandi"], None] = None,
    checks: Union[list, None] = None,
    ignore: Union[list[str], None] = None,
    select: Union[list[str], None] = None,
    importance_threshold: Union[str, Importance] = Importance.BEST_PRACTICE_SUGGESTION,
    skip_validate: bool = False,
    show_progress_bar: bool = True,
    client: Union["dandi.dandiapi.DandiAPIClient", None] = None,  # type: ignore
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Inspect a Dandiset for common issues.

    Parameters
    ----------
    dandiset_id : six-digit string, "draft", or None
        The six-digit ID of the Dandiset to inspect.
    dandiset_version : string
        The specific published version of the Dandiset to inspect.
        If None, the latest version is used.
        If there are no published versions, then 'draft' is used instead.
    config : file path, dictionary, or "dandi", default: "dandi"
        If a file path, loads the dictionary configuration from the file.
        If a dictionary, it must be valid against the configuration schema.
        If "dandi", uses the requirements for DANDI validation.
    checks : list, optional
        list of checks to run
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
    skip_validate : bool, default: False
        Skip the PyNWB validation step.
        This may be desired for older NWBFiles (< schema version v2.10).
    show_progress_bar : bool, optional
        Whether to display a progress bar while scanning the assets on the Dandiset.
    client: dandi.dandiapi.DandiAPIClient
        The client object can be passed to avoid re-instantiation over an iteration.
    """
    config = config or "dandi"

    if client is None:
        import dandi.dandiapi

        client = dandi.dandiapi.DandiAPIClient()

    dandiset = client.get_dandiset(dandiset_id=dandiset_id, version_id=dandiset_version)

    nwb_assets = [asset for asset in dandiset.get_assets() if ".nwb" in pathlib.Path(asset.path).suffixes]

    nwb_assets_iterator = nwb_assets
    if show_progress_bar:
        import tqdm

        nwb_assets_iterator = tqdm.tqdm(
            iterable=nwb_assets, total=len(nwb_assets), desc="Inspecting NWB files", unit="file", position=0, leave=True
        )

    for asset in nwb_assets_iterator:
        asset_url = asset.get_content_url(follow_redirects=1, strip_query=True)

        for message in inspect_url(
            url=asset_url,
            config=config,
            checks=checks,
            ignore=ignore,
            select=select,
            importance_threshold=importance_threshold,
            skip_validate=skip_validate,
        ):
            message.file_path = asset.path  # type: ignore
            yield message


def inspect_dandi_file_path(
    *,
    dandi_file_path: str,
    dandiset_id: str,
    dandiset_version: Union[str, Literal["draft"], None] = None,
    config: Union[str, pathlib.Path, dict, Literal["dandi"], None] = "dandi",
    checks: Union[list, None] = None,
    ignore: Union[list[str], None] = None,
    select: Union[list[str], None] = None,
    importance_threshold: Union[str, Importance] = Importance.BEST_PRACTICE_SUGGESTION,
    skip_validate: bool = False,
    client: Union["dandi.dandiapi.DandiAPIClient", None] = None,  # type: ignore
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Inspect a Dandifile for common issues.

    Parameters
    ----------
    dandi_file_path : string
        The path to the Dandifile as seen on the archive; e.g., 'sub-123_ses-456+ecephys.nwb'.
    dandiset_id : six-digit string, "draft", or None
        The six-digit ID of the Dandiset.
    dandiset_version : string
        The specific published version of the Dandiset to inspect.
        If None, the latest version is used.
        If there are no published versions, then 'draft' is used instead.
    config : file path, dictionary, "dandi", or None, default: "dandi"
        If a file path, loads the dictionary configuration from the file.
        If a dictionary, it must be valid against the configuration schema.
        If "dandi", uses the requirements for DANDI validation.
    checks : list, optional
        list of checks to run
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
    skip_validate : bool, default: False
        Skip the PyNWB validation step.
        This may be desired for older NWBFiles (< schema version v2.10).
    client: dandi.dandiapi.DandiAPIClient
        The client object can be passed to avoid re-instantiation over an iteration.
    """
    if client is None:
        import dandi.dandiapi

        client = dandi.dandiapi.DandiAPIClient()

    dandiset = client.get_dandiset(dandiset_id=dandiset_id, version_id=dandiset_version)
    asset = dandiset.get_asset_by_path(path=dandi_file_path)
    asset_url = asset.get_content_url(follow_redirects=1, strip_query=True)

    for message in inspect_url(
        url=asset_url,
        config=config,
        checks=checks,
        ignore=ignore,
        select=select,
        importance_threshold=importance_threshold,
        skip_validate=skip_validate,
    ):
        message.file_path = dandi_file_path  # type: ignore
        yield message


def inspect_url(
    *,
    url: str,
    config: Union[str, pathlib.Path, dict, Literal["dandi"], None] = "dandi",
    checks: Union[list, None] = None,
    ignore: Union[list[str], None] = None,
    select: Union[list[str], None] = None,
    importance_threshold: Union[str, Importance] = Importance.BEST_PRACTICE_SUGGESTION,
    skip_validate: bool = False,
) -> Iterable[Union[InspectorMessage, None]]:
    """
    Inspect an explicit S3 URL.

    Parameters
    ----------
    url : string
        A URL referring to the cloud location of an NWB file.
        Commonly used with DANDI, where the URL has a form similar to:
        https://dandiarchive.s3.amazonaws.com/blobs/636/57e/63657e32-ad33-4625-b664-31699b5bf664

        Note: this must be the `https` URL, not the 's3://' form.
    config : file path, dictionary, "dandi", or None, default: "dandi"
        If a file path, loads the dictionary configuration from the file.
        If a dictionary, it must be valid against the configuration schema.
        If "dandi", uses the requirements for DANDI validation.
    checks : list, optional
        list of checks to run
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
    skip_validate : bool, default: False
        Whether to skip the PyNWB validation step.
    """
    import remfile

    filterwarnings(action="ignore", message="No cached namespaces found in .*")
    filterwarnings(action="ignore", message="Ignoring cached namespace .*")

    if isinstance(config, (str, pathlib.Path)):
        config = load_config(filepath_or_keyword=config)
    if isinstance(config, dict):
        validate_config(config=config)

    byte_stream = remfile.File(url=url)
    with (
        h5py.File(name=byte_stream) as file,
        pynwb.NWBHDF5IO(file=file) as io,
    ):
        if skip_validate is False:
            validation_errors = pynwb.validate(io=io)
            for validation_error in validation_errors:
                yield InspectorMessage(
                    message=validation_error.reason,
                    importance=Importance.PYNWB_VALIDATION,
                    check_function_name=validation_error.name,
                    location=validation_error.location,
                    file_path=url,
                )

        nwbfile = io.read()

        for message in inspect_nwbfile_object(
            nwbfile_object=nwbfile,
            config=config,
            checks=checks,
            ignore=ignore,
            select=select,
            importance_threshold=importance_threshold,
        ):
            message.file_path = url  # type: ignore
            yield message
