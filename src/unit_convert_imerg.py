# scripts/unit_convert_imerg.py

import xarray as xr
from src.config import (
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    IMERG_RAW_DIR,
    START_DATE,
    END_DATE,
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
    IMERG_CONCAT_FILE,
    IMERG_MM_DAY_FILE,
    GPCP_SUBSET_FILE,
)



def main():
    ds = xr.open_dataset(IMERG_CONCAT_FILE)

    pr_mm_day = ds["precip_mm_hr"] * 24.0
    pr_mm_day.attrs["units"] = "mm/day"
    pr_mm_day.attrs["description"] = "IMERG monthly precipitation converted from mm/hr"

    out = pr_mm_day.to_dataset(name="precip_mm_day")
    out.to_netcdf(IMERG_MM_DAY_FILE)

    print("Saved:", IMERG_MM_DAY_FILE)

if __name__ == "__main__":
    main()
