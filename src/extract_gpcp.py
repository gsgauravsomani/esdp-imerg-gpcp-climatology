# src/extract_gpcp.py

from pathlib import Path
import xarray as xr

from src.config import (
    RAW_DIR,
    PROCESSED_DIR,
    START_DATE,
    END_DATE,
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
    GPCP_SUBSET_FILE,
)

def main():
    gpcp_dir = RAW_DIR / "gpcp_monthly"
    files = sorted(gpcp_dir.glob("gpcp_v02r03_monthly_*.nc"))

    if not files:
        raise RuntimeError(f"No GPCP files found in {gpcp_dir}")

    print(f"Found {len(files)} GPCP monthly files")

    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        data_vars="minimal",
        coords="minimal",
        compat="override"
    )

    # Select precipitation
    da = ds["precip"]

    # Time subset
    da = da.sel(time=slice(START_DATE, END_DATE))

    # Spatial subset (latitude is ascending in this GPCP file set)
    da = da.sel(
        latitude=slice(LAT_MIN, LAT_MAX),
        longitude=slice(LON_MIN, LON_MAX)
    )

    # Convert to Dataset BEFORE dropping bounds
    out_ds = da.to_dataset(name="precip_mm_day")

    # Drop bounds if present
    for v in ["time_bnds", "lat_bnds", "lon_bnds"]:
        if v in out_ds.coords:
            out_ds = out_ds.drop_vars(v)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_ds.to_netcdf(GPCP_SUBSET_FILE)

    print("Saved:", GPCP_SUBSET_FILE.resolve())

if __name__ == "__main__":
    main()
