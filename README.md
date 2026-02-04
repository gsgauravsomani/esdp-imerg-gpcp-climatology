# IMERG–GPCP Monthly Precipitation Climatology  
**ESDP Final Project**

## Project Overview

This project compares two widely used **global monthly precipitation datasets** over **Northern India**:

- **IMERG Final Run (GPM, Version 07)**
- **GPCP Monthly Climate Data Record (Version 2.3)**

The goal is to evaluate **spatial and temporal agreement** between these products after harmonizing:
- spatial resolution,
- coordinate conventions,
- units,
- and time handling.

The final outputs include regridded datasets, sanity-check metrics, and diagnostic plots suitable for climatological comparison.

---

## Why this project is relevant

Merged satellite–gauge precipitation products are widely used for:
- regional climatology,
- model validation,
- climate variability studies.

However, these products differ in resolution, longitude conventions, and data sources.  
A careful and reproducible preprocessing workflow is therefore required before comparison.  
This project demonstrates such a workflow end-to-end.

---

## Time period selection (2019–2021)

The analysis focuses on **January 2019 – December 2021**.

Reasons:
- Both IMERG and GPCP provide stable, well-documented coverage.
- A 3-year window captures full seasonal cycles (including monsoon variability).
- Longer periods (e.g. 7+ years) were initially explored but proved computationally heavy for an exploratory ESDP project.

This period also overlaps with the **COVID-19 era**, motivating future extensions.

---

## Datasets used

### IMERG (Integrated Multi-satellitE Retrievals for GPM)

- Product: IMERG Final Run Monthly (V07)
- Resolution: ~0.1°
- Coverage: global
- Native units: mm/hr (monthly mean rate)

**Download source:**  
https://gpm.nasa.gov/data/directory  

**Access method:**  
Authenticated HTTPS download from NASA GES DISC using `.netrc`, implemented in the exploratory notebook.

---

### GPCP (Global Precipitation Climatology Project)

- Product: GPCP Monthly CDR V2.3
- Resolution: 2.5° × 2.5°
- Coverage: global
- Units: mm/day

**Download source:**  
https://www.ncei.noaa.gov/data/global-precipitation-climatology-project-gpcp-monthly/access/

**Access method:**  
Manual download of monthly NetCDF files (2019–2021).

---

## Exploratory notebook

The notebook `Exploratory-Notebook.ipynb` documents:
- file structure and metadata inspection,
- variable names and units,
- coordinate conventions (lat/lon order, 0–360 vs −180–180),
- time encoding and monthly resolution,
- data volume considerations.

This notebook is **purely exploratory**.  
All final processing steps are implemented in scripts under `src/`.

---

## Data volume (approximate)

**Initially downloaded (global):**
- IMERG monthly (2019–2021): ~36 files × ~17–19 MB ≈ **~648 MB**
- GPCP monthly (2019–2021): ~36 files × ~110 KB ≈ **~4 MB**

**After processing (Northern India subset):**
- IMERG subset: tens of MB
- GPCP subset: few MB
- Regridded IMERG: small, GPCP-sized grid

Raw global files are preserved during concatenation and can be removed after processed outputs are created.

---

## Project structure
```text
ESDP-final-project/
│
├── data/
│ ├── raw/
│ │ ├── imerg_monthly/
│ │ └── gpcp_monthly/
│ └── processed/
│ ├── imerg_north_india.nc
│ ├── imerg_north_india_mmday.nc
│ ├── gpcp_north_india.nc
│ ├── imerg_north_india_on_gpcp_grid.nc
│ └── regrid_sanity_check_report.json
│
├── notebooks/
│ └── Exploratory-Notebook.ipynb
│
├── src/
│ ├── config.py
│ ├── concatenate_imerg.py
│ ├── unit_convert_imerg.py
│ ├── extract_gpcp.py
│ ├── regrid_imerg_to_gpcp.py
│ ├── sanity_check_regrid.py
│ ├── make_plots.py
│ └── run_pipeline.py
│
├── plots/
│ └── *.png
│
├── requirements.txt
└── README.md
```
## ESDP Final Project: IMERG vs GPCP Precipitation Analysis (Northern India, 2019-2021)

This project builds a reproducible precipitation comparison workflow for Northern India using two independent monthly products:

- **IMERG** (satellite-based, NASA GPM mission)
- **GPCP** (merged gauge + satellite climatology product from the Global Precipitation Climatology Project, coordinated under WCRP/NOAA data production streams)

The goal is to compare both datasets on a common domain and common grid, then evaluate agreement with maps and metrics.

---

## 1) Study Domain and Time Window

- **Region:** 20N-35N, 68E-90E (Northern India bounding box)
- **Period:** January 2019 to December 2021 (36 monthly steps)
- **Working units:** `mm/day` (monthly mean daily precipitation rate)

All core settings are controlled in `src/config.py`.

---

## 2) Dataset Sources and Variables Used

### IMERG (GPM)
- Raw files: monthly HDF5 in `data/raw/imerg_monthly/`
- File pattern expected by pipeline: `3B-MO.MS.MRG.3IMERG.*.HDF5`
- Variable extracted from `Grid` group: `precipitation`
- Saved intermediate variable name: `precip_mm_hr` (from IMERG)
- Converted variable: `precip_mm_day`

### GPCP Monthly
- Raw files: monthly NetCDF in `data/raw/gpcp_monthly/`
- File pattern expected by pipeline: `gpcp_v02r03_monthly_*.nc`
- Variable extracted: `precip`
- Saved variable name for processing: `precip_mm_day`

### Final variables compared
- `imerg_precip_mm_day` (IMERG regridded to GPCP grid)
- `precip_mm_day` (GPCP subset)

---

## 3) How the Dataset Was Formed and Treated

The pipeline does the following:

1. **Concatenate IMERG monthly files** (`src/concatenate_imerg.py`)
   - Opens all monthly files with `xarray.open_mfdataset`
   - Selects time and regional subset
   - Writes `data/processed/imerg_north_india.nc`

2. **Convert IMERG units** (`src/unit_convert_imerg.py`)
   - Converts `mm/hr` to `mm/day` by multiplying by `24`
   - Writes `data/processed/imerg_north_india_mmday.nc`

3. **Extract GPCP subset** (`src/extract_gpcp.py`)
   - Opens all monthly GPCP files
   - Applies the same time and regional subset
   - Drops bounds coordinates if present (`time_bnds`, `lat_bnds`, `lon_bnds`)
   - Writes `data/processed/gpcp_north_india.nc`

4. **Regrid IMERG to GPCP grid** (`src/regrid_imerg_to_gpcp.py`)
   - Renames IMERG dimensions (`lat/lon` -> `latitude/longitude`)
   - Converts longitude if needed (`-180..180` -> `0..360`)
   - Interpolates IMERG onto GPCP grid with linear interpolation
   - Writes `data/processed/imerg_north_india_on_gpcp_grid.nc`

5. **Sanity checks and metrics** (`src/sanity_check_regrid.py`)
   - Ensures common grid/time alignment
   - Computes bias/MAE/RMSE/correlation on area-mean monthly series
   - Writes report JSON: `data/processed/regrid_sanity_check_report.json`

---

## 4) Regridding: What Actually Happened

IMERG has finer native resolution than GPCP. To compare like-for-like:

- IMERG was interpolated to the coarser GPCP grid (`latitude`, `longitude`)
- Method used: `xarray.interp(..., method="linear")`
- Output shape after regrid matches GPCP: `(time, latitude, longitude) = (36, 6, 9)`

This step is essential: without common grid alignment, grid-cell comparisons and bias maps are not physically consistent.

---

## 5) Raw Data Difficulties Encountered

Typical issues this workflow handles:

- Different file formats and structures (IMERG HDF5 group-based vs GPCP NetCDF)
- Different coordinate names (`lat/lon` vs `latitude/longitude`)
- Longitude conventions mismatch (`-180..180` vs `0..360`)
- Presence of extra bounds coordinates in GPCP files
- Need to standardize units before comparison (`mm/hr` vs `mm/day`)

The pipeline resolves these issues programmatically so the analysis is repeatable.

---

## 6) What the Sanity Checks Evaluate

Sanity checks verify:

- Shape consistency after alignment
- Latitude/longitude grid identity
- Shared time-step count
- Value ranges and NaN counts
- Agreement metrics on area-mean monthly series:
  - **Bias** (`IMERG - GPCP`)
  - **MAE**
  - **RMSE**
  - **Pearson correlation**

This catches misalignment or unit/coordinate errors before plotting or interpretation.

---

## 7) Plot Outputs

Generated by `src/make_plots.py`:

- `plots/mean_precip_imerg_vs_gpcp.png`
- `plots/mean_bias_imerg_minus_gpcp.png`
- `plots/area_mean_timeseries.png`
- `plots/rmse_map_imerg_vs_gpcp.png`
- `plots/jjas_bias_imerg_minus_gpcp.png`

Map plots use Cartopy and include:
- Latitude/longitude labels
- Coastline and borders
- India boundary outline (Natural Earth geometry)
- Labeled colorbars in `mm/day`

---

## 8) Reproducibility and Scalability Opportunity

Why this project is reproducible:

- Central configuration in `src/config.py`
- Scripted preprocessing and evaluation modules
- Deterministic outputs to `data/processed/` and `plots/`
- Smoke tests in `tests/test_pipeline_smoke.py`

Why this can scale:

- Extend date windows in config
- Expand region bounds in config
- Add new metrics/plots without changing core ingestion/regridding logic
- Adapt to additional products by adding one extraction module + same common-grid strategy

---

## 9) Project Structure

```text
data/
  raw/
    imerg_monthly/
    gpcp_monthly/
  processed/
src/
  config.py
  run_pipeline.py
  concatenate_imerg.py
  unit_convert_imerg.py
  extract_gpcp.py
  regrid_imerg_to_gpcp.py
  sanity_check_regrid.py
  make_plots.py
plots/
tests/
```

---

## 10) How To Run

### A. Environment setup
```bash
pip install -r requirements.txt
```

### B. Prepare raw data
1. Download IMERG monthly files (per project notebook guidance) into:
   - `data/raw/imerg_monthly/`
2. Manually download GPCP monthly files into:
   - `data/raw/gpcp_monthly/`

Ensure filenames match expected patterns listed above.

### C. Run full processing pipeline
```bash
python -m src.run_pipeline
```

### D. Generate plots
```bash
python -m src.make_plots
```

### E. Optional tests
```bash
python -m pytest -q
```

---

## 11) Config-Driven Usage (`src/config.py`)

You can change:

- `START_DATE`, `END_DATE` for period
- `LAT_MIN`, `LAT_MAX`, `LON_MIN`, `LON_MAX` for domain
- Output paths for processed files

Then rerun pipeline + plotting scripts to regenerate all products consistently.
