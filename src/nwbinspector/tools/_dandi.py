"""Helper functions related to DANDI for internal use that rely on external dependencies (i.e., dandi)."""

import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional

from ..utils import calculate_number_of_cpu, is_module_installed


def get_s3_urls_and_dandi_paths(dandiset_id: str, version_id: Optional[str] = None, n_jobs: int = 1) -> dict[str, str]:
    """
    Collect S3 URLS from a DANDISet ID.

    Returns dictionary that maps each S3 url to the displayed file path on the DANDI archive content page.
    """
    assert is_module_installed(module_name="dandi"), "You must install DANDI to get S3 paths (pip install dandi)."
    from dandi.dandiapi import DandiAPIClient

    assert re.fullmatch(
        pattern="^[0-9]{6}$", string=dandiset_id
    ), "The specified 'path' is not a proper DANDISet ID. It should be a six-digit numeric identifier."

    s3_urls_to_dandi_paths = dict()
    n_jobs = calculate_number_of_cpu(requested_cpu=n_jobs)
    if n_jobs != 1:
        with DandiAPIClient() as client:
            dandiset = client.get_dandiset(dandiset_id=dandiset_id, version_id=version_id)
            max_workers = n_jobs if n_jobs > 0 else None
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for asset in dandiset.get_assets():
                    if asset.path.split(".")[-1] == "nwb":
                        futures.append(
                            executor.submit(
                                _get_content_url_and_path, asset=asset, follow_redirects=1, strip_query=True
                            )
                        )
                    for future in as_completed(futures):
                        s3_urls_to_dandi_paths.update(future.result())
    else:
        with DandiAPIClient() as client:
            dandiset = client.get_dandiset(dandiset_id=dandiset_id, version_id=version_id)
            for asset in dandiset.get_assets():
                if asset.path.split(".")[-1] == "nwb":
                    s3_urls_to_dandi_paths.update(_get_content_url_and_path(asset=asset))
    return s3_urls_to_dandi_paths


def _get_content_url_and_path(
    asset: "dandi.dandiapi.BaseRemoteAsset",  # type: ignore
    follow_redirects: int = 1,
    strip_query: bool = True,
) -> dict[str, str]:
    """
    Private helper function for parallelization in 'get_s3_urls_and_dandi_paths'.

    Must be globally defined (not as a part of get_s3_urls..) in order to be pickled.
    """
    return {asset.get_content_url(follow_redirects=1, strip_query=True): asset.path}
