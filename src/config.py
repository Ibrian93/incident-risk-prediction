"""Shared paths for local and Docker execution."""
import os
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parents[1]))
DUCKDB_PATH = Path(os.environ.get("DUCKDB_PATH", PROJECT_ROOT / "data/processed/safety.duckdb"))
ZIP_PATH = PROJECT_ROOT / "data/raw/osha_severe_injuries.zip"
SOURCE_ZIP_PATH = Path(os.environ.get(
    "SOURCE_ZIP_PATH", PROJECT_ROOT / "January2015toOctober2025.zip"
))
DBT_PROFILES_DIR = Path(os.environ.get("DBT_PROFILES_DIR", PROJECT_ROOT / "config/dbt"))
