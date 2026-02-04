# src/concatenate_imerg.py

from pathlib import Path
import xarray as xr

from src.config import (
    IMERG_RAW_DIR,
    START_DATE,
    END_DATE,
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
)

# -------------------------------------------------------------------
# Resolve project root and output path
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "imerg_north_india.nc"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# IMERG_RAW_DIR = Path(r"D:\esdp\ESDP-final-project\data\raw\imerg_monthly")


def main():
    # ----------------------------------------------------------------
    # Collect IMERG monthly files
    # ----------------------------------------------------------------
    files = sorted(
        IMERG_RAW_DIR.glob("3B-MO.MS.MRG.3IMERG.*.HDF5")
    )

    if not files:
        raise RuntimeError(f"No IMERG files found in {IMERG_RAW_DIR}")

    print(f"Found {len(files)} IMERG files")

    # ----------------------------------------------------------------
    # Open and concatenate
    # ----------------------------------------------------------------
    ds = xr.open_mfdataset(
        files,
        engine="netcdf4",
        group="Grid",
        combine="by_coords",
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )

    pr = ds["precipitation"]

    # ----------------------------------------------------------------
    # Subset time (monthly timestamps)
    # ----------------------------------------------------------------
    pr = pr.sel(time=slice(START_DATE, END_DATE))

    # ----------------------------------------------------------------
    # Subset space (IMERG uses -180 to 180 longitude)
    # ----------------------------------------------------------------
    pr = pr.sel(
        lat=slice(LAT_MIN, LAT_MAX),
        lon=slice(LON_MIN, LON_MAX),
    )

    # ----------------------------------------------------------------
    # Save processed dataset
    # ----------------------------------------------------------------
    out = pr.to_dataset(name="precip_mm_hr")
    out.to_netcdf(OUT_PATH)

    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
