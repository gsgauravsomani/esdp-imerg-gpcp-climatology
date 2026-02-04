# config.py

from pathlib import Path

# ------------------
# Base paths
# ------------------
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

IMERG_RAW_DIR = RAW_DIR / "imerg_monthly"

# ------------------
# Time configuration
# ------------------
START_DATE = "2019-01-01"
END_DATE   = "2021-12-01"

# ------------------
# Northern India domain
# ------------------
LAT_MIN = 20.0
LAT_MAX = 35.0

LON_MIN = 68.0
LON_MAX = 90.0

# ------------------
# Output files
# ------------------
IMERG_CONCAT_FILE = PROCESSED_DIR / "imerg_north_india.nc"
IMERG_MM_DAY_FILE = PROCESSED_DIR / "imerg_north_india_mmday.nc"
GPCP_SUBSET_FILE  = PROCESSED_DIR / "gpcp_north_india.nc"
