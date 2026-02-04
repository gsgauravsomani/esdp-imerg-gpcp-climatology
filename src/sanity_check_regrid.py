import json
from pathlib import Path

import numpy as np
import xarray as xr

from src.config import GPCP_SUBSET_FILE, PROCESSED_DIR


def main():
    imerg_regridded_file = PROCESSED_DIR / "imerg_north_india_on_gpcp_grid.nc"
    report_file = PROCESSED_DIR / "regrid_sanity_check_report.json"

    im = xr.open_dataset(imerg_regridded_file)["imerg_precip_mm_day"]
    gp = xr.open_dataset(GPCP_SUBSET_FILE)["precip_mm_day"]

    # Force shared time dtype/values for stable alignment and comparison.
    if im.sizes["time"] == gp.sizes["time"]:
        im = im.assign_coords(time=gp["time"].values)

    im_a, gp_a = xr.align(im, gp, join="inner")

    im_m = im_a.mean(dim=("latitude", "longitude"))
    gp_m = gp_a.mean(dim=("latitude", "longitude"))
    diff = im_m - gp_m

    results = {
        "files": {
            "imerg_regridded": str(imerg_regridded_file),
            "gpcp_subset": str(GPCP_SUBSET_FILE),
        },
        "shape_checks": {
            "imerg_shape": list(im_a.shape),
            "gpcp_shape": list(gp_a.shape),
            "common_time_steps": int(im_a.sizes["time"]),
            "same_latitude_grid": bool(
                np.array_equal(im_a["latitude"].values, gp_a["latitude"].values)
            ),
            "same_longitude_grid": bool(
                np.array_equal(im_a["longitude"].values, gp_a["longitude"].values)
            ),
        },
        "value_checks": {
            "imerg": {
                "min_mm_day": float(np.nanmin(im_a.values)),
                "max_mm_day": float(np.nanmax(im_a.values)),
                "mean_mm_day": float(np.nanmean(im_a.values)),
                "nan_count": int(np.isnan(im_a.values).sum()),
            },
            "gpcp": {
                "min_mm_day": float(np.nanmin(gp_a.values)),
                "max_mm_day": float(np.nanmax(gp_a.values)),
                "mean_mm_day": float(np.nanmean(gp_a.values)),
                "nan_count": int(np.isnan(gp_a.values).sum()),
            },
        },
        "monthly_spatial_mean_metrics": {
            "bias_mm_day_imerg_minus_gpcp": float(diff.mean().values),
            "mae_mm_day": float(np.abs(diff).mean().values),
            "rmse_mm_day": float(np.sqrt((diff**2).mean().values)),
            "pearson_r": float(np.corrcoef(im_m.values, gp_m.values)[0, 1]),
        },
    }

    first5 = []
    for t, iv, gv in zip(im_m["time"].values[:5], im_m.values[:5], gp_m.values[:5]):
        first5.append(
            {
                "time": str(t)[:10],
                "imerg_mean_mm_day": float(iv),
                "gpcp_mean_mm_day": float(gv),
                "diff_mm_day": float(iv - gv),
            }
        )
    results["first_5_months_area_mean"] = first5

    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("Sanity checks complete")
    print(f"Saved report: {report_file}")
    print(json.dumps(results["monthly_spatial_mean_metrics"], indent=2))


if __name__ == "__main__":
    main()
