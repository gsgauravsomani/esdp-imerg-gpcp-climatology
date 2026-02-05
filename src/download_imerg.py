"""Utilities to prepare IMERG monthly files.

This module supports a dry-run mode so pipeline checks can run without
triggering network downloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import requests

from src.config import IMERG_RAW_DIR

IMERG_GLOB = "3B-MO.MS.MRG.3IMERG.*.HDF5"


@dataclass(frozen=True)
class DownloadResult:
    existing_files: int
    downloaded_files: int
    attempted_urls: int


def list_local_files(raw_dir: Path = IMERG_RAW_DIR) -> List[Path]:
    return sorted(raw_dir.glob(IMERG_GLOB))


def ensure_imerg_data(
    raw_dir: Path = IMERG_RAW_DIR,
    *,
    download: bool = False,
    urls: list[str] | None = None,
    timeout: int = 60,
) -> DownloadResult:
    """Ensure IMERG files are present.

    When ``download`` is False, this function only checks local files and never
    performs a network request.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    local_files = list_local_files(raw_dir)
    if local_files:
        return DownloadResult(
            existing_files=len(local_files),
            downloaded_files=0,
            attempted_urls=0,
        )

    if not download:
        raise RuntimeError(
            f"No IMERG files found in {raw_dir}. "
            "Re-run with download=True and a URL list to fetch files."
        )

    candidate_urls = urls or []
    downloaded = 0
    for url in candidate_urls:
        target = raw_dir / Path(url).name
        if target.exists():
            continue
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        target.write_bytes(response.content)
        downloaded += 1

    return DownloadResult(
        existing_files=len(list_local_files(raw_dir)),
        downloaded_files=downloaded,
        attempted_urls=len(candidate_urls),
    )


def main():
    result = ensure_imerg_data(download=False)
    print(
        "IMERG ready:",
        f"existing={result.existing_files}",
        f"downloaded={result.downloaded_files}",
    )


if __name__ == "__main__":
    main()
