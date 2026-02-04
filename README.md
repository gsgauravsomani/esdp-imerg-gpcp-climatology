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
