from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import xarray as xr

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader

from src.config import GPCP_SUBSET_FILE, PROCESSED_DIR


PLOTS_DIR = Path("plots")
IMERG_REGRID_FILE = PROCESSED_DIR / "imerg_north_india_on_gpcp_grid.nc"
LON_MIN, LON_MAX = 68.0, 90.0
LAT_MIN, LAT_MAX = 20.0, 35.0


def _load_data():
    imerg = xr.open_dataset(IMERG_REGRID_FILE)["imerg_precip_mm_day"]
    gpcp = xr.open_dataset(GPCP_SUBSET_FILE)["precip_mm_day"]
    imerg, gpcp = xr.align(imerg, gpcp, join="inner")
    return imerg, gpcp


def _india_geometry():
    shp = shapereader.natural_earth(
        resolution="50m", category="cultural", name="admin_0_countries"
    )
    reader = shapereader.Reader(shp)
    for record in reader.records():
        if record.attributes.get("ADMIN") == "India":
            return record.geometry
    raise RuntimeError("India geometry not found in Natural Earth dataset.")


def _style_map_axis(ax, india_geom):
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="#f6f3ea", edgecolor="none", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor="#3a3a3a", zorder=3)
    ax.add_feature(cfeature.BORDERS, linewidth=0.7, edgecolor="#4a4a4a", zorder=3)
    ax.add_geometries(
        [india_geom],
        crs=ccrs.PlateCarree(),
        facecolor="none",
        edgecolor="black",
        linewidth=1.4,
        zorder=4,
    )

    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=0.5,
        color="#8a8a8a",
        alpha=0.6,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator([70, 75, 80, 85, 90])
    gl.ylocator = mticker.FixedLocator([20, 25, 30, 35])
    gl.xlabel_style = {"size": 9}
    gl.ylabel_style = {"size": 9}


def plot_mean_maps(imerg, gpcp, india_geom):
    imerg_mean = imerg.mean("time")
    gpcp_mean = gpcp.mean("time")

    vmax = float(np.nanpercentile(np.concatenate([imerg_mean.values.ravel(), gpcp_mean.values.ravel()]), 98))
    vmax = max(vmax, 1.0)

    fig, axs = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(14, 5.4),
        subplot_kw={"projection": ccrs.PlateCarree()},
        constrained_layout=True,
    )

    cmap = plt.get_cmap("YlGnBu")
    fields = [imerg_mean, gpcp_mean]
    titles = [
        "IMERG Mean Precipitation (2019-2021)",
        "GPCP Mean Precipitation (2019-2021)",
    ]

    mappable = None
    for ax, field, title in zip(axs, fields, titles):
        _style_map_axis(ax, india_geom)
        mappable = ax.pcolormesh(
            field["longitude"],
            field["latitude"],
            field,
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            vmin=0.0,
            vmax=vmax,
            shading="auto",
        )
        ax.set_title(title, fontsize=11, weight="semibold")

    cbar = fig.colorbar(
        mappable,
        ax=axs,
        orientation="vertical",
        shrink=0.88,
        pad=0.02,
    )
    cbar.set_label("Precipitation (mm/day)", fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    out_file = PLOTS_DIR / "mean_precip_imerg_vs_gpcp.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_file}")


def plot_bias_map(imerg, gpcp, india_geom):
    bias = (imerg - gpcp).mean("time")
    vmax = float(np.nanpercentile(np.abs(bias.values), 98))
    vmax = max(vmax, 0.5)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(9.2, 5.4),
        subplot_kw={"projection": ccrs.PlateCarree()},
        constrained_layout=True,
    )
    _style_map_axis(ax, india_geom)

    mappable = ax.pcolormesh(
        bias["longitude"],
        bias["latitude"],
        bias,
        transform=ccrs.PlateCarree(),
        cmap="RdBu_r",
        norm=norm,
        shading="auto",
    )
    ax.set_title("Mean Bias: IMERG - GPCP (2019-2021)", fontsize=11, weight="semibold")

    cbar = fig.colorbar(mappable, ax=ax, orientation="vertical", shrink=0.9, pad=0.03)
    cbar.set_label("Bias (mm/day)", fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    out_file = PLOTS_DIR / "mean_bias_imerg_minus_gpcp.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_file}")


def plot_area_mean_timeseries(imerg, gpcp):
    imerg_ts = imerg.mean(dim=("latitude", "longitude"))
    gpcp_ts = gpcp.mean(dim=("latitude", "longitude"))

    fig, ax = plt.subplots(figsize=(11.5, 4.8), constrained_layout=True)
    ax.plot(
        imerg_ts["time"],
        imerg_ts,
        color="#1f77b4",
        linewidth=2.2,
        label="IMERG (regridded)",
    )
    ax.plot(
        gpcp_ts["time"],
        gpcp_ts,
        color="#d95f02",
        linewidth=2.2,
        label="GPCP",
    )

    ax.set_title(
        "Northern India Area-Averaged Monthly Precipitation (2019-2021)",
        fontsize=11,
        weight="semibold",
    )
    ax.set_xlabel("Time", fontsize=10)
    ax.set_ylabel("Precipitation (mm/day)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(frameon=False)

    out_file = PLOTS_DIR / "area_mean_timeseries.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_file}")


def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    imerg, gpcp = _load_data()
    india_geom = _india_geometry()

    plot_mean_maps(imerg, gpcp, india_geom)
    plot_bias_map(imerg, gpcp, india_geom)
    plot_area_mean_timeseries(imerg, gpcp)
    print("Done: generated 3 plots in ./plots")


if __name__ == "__main__":
    main()
