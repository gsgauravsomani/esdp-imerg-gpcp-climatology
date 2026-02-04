# src/regrid_imerg_to_gpcp.py

import xarray as xr

from src.config import (
    PROCESSED_DIR,
    IMERG_MM_DAY_FILE,
    GPCP_SUBSET_FILE,
)


def main():
    # Load datasets
    imerg = xr.open_dataset(IMERG_MM_DAY_FILE)
    gpcp = xr.open_dataset(GPCP_SUBSET_FILE)

    da = imerg["precip_mm_day"]

    # Standardize IMERG dimension names to match GPCP coordinate names.
    rename_map = {}
    if "lat" in da.dims:
        rename_map["lat"] = "latitude"
    if "lon" in da.dims:
        rename_map["lon"] = "longitude"
    if rename_map:
        da = da.rename(rename_map)

    # Convert longitude from -180..180 to 0..360 when needed.
    if float(da["longitude"].min()) < 0:
        da = da.assign_coords(
            longitude=(da["longitude"] % 360)
        ).sortby("longitude")

    # Interpolate IMERG onto GPCP grid
    imerg_interp = da.interp(
        latitude=gpcp["latitude"],
        longitude=gpcp["longitude"],
        method="linear",
    )
    if imerg_interp.sizes.get("time") == gpcp.sizes.get("time"):
        imerg_interp = imerg_interp.assign_coords(time=gpcp["time"].values)
    imerg_interp = imerg_interp.transpose("time", "latitude", "longitude")

    # Save output
    out = imerg_interp.to_dataset(name="imerg_precip_mm_day")
    out.attrs["note"] = (
        "IMERG monthly precipitation (mm/day) "
        "regridded to GPCP 2.5 degree grid using xarray.interp"
    )

    out_file = PROCESSED_DIR / "imerg_north_india_on_gpcp_grid.nc"
    out.to_netcdf(out_file)

    print("Regridding complete")
    print("Saved:", out_file.resolve())


if __name__ == "__main__":
    main()
