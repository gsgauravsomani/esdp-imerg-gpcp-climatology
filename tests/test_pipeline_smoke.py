from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from src.config import GPCP_SUBSET_FILE, IMERG_MM_DAY_FILE, PROCESSED_DIR


def _require_file(path: Path):
    if not path.exists():
        pytest.skip(f"Missing required file: {path}")


def test_processed_files_exist():
    files = [
        IMERG_MM_DAY_FILE,
        GPCP_SUBSET_FILE,
        PROCESSED_DIR / "imerg_north_india_on_gpcp_grid.nc",
    ]
    for f in files:
        assert f.exists(), f"Expected file not found: {f}"


def test_regridded_dims_match_gpcp():
    regrid_file = PROCESSED_DIR / "imerg_north_india_on_gpcp_grid.nc"
    _require_file(regrid_file)
    _require_file(GPCP_SUBSET_FILE)

    im = xr.open_dataset(regrid_file)["imerg_precip_mm_day"]
    gp = xr.open_dataset(GPCP_SUBSET_FILE)["precip_mm_day"]

    if im.sizes["time"] == gp.sizes["time"]:
        im = im.assign_coords(time=gp["time"].values)
    im_a, gp_a = xr.align(im, gp, join="inner")

    assert im_a.shape == gp_a.shape
    assert np.array_equal(im_a["latitude"].values, gp_a["latitude"].values)
    assert np.array_equal(im_a["longitude"].values, gp_a["longitude"].values)


def test_regridded_has_no_nans():
    regrid_file = PROCESSED_DIR / "imerg_north_india_on_gpcp_grid.nc"
    _require_file(regrid_file)

    da = xr.open_dataset(regrid_file)["imerg_precip_mm_day"]
    assert int(np.isnan(da.values).sum()) == 0
