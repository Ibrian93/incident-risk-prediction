from pathlib import Path
import zipfile
import pandas as pd
import duckdb

from config import ZIP_PATH, DUCKDB_PATH
TABLE_NAME = "bronze.raw_severe_injuries"


def load_csv_from_zip(zip_path: Path) -> pd.DataFrame:
    if not zip_path.exists():
        raise FileNotFoundError(f"Missing file: {zip_path}. Run `python src/download_data.py` first.")
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        csv_files = [name for name in zip_file.namelist() if name.lower().endswith(".csv")]

        if len(csv_files) != 1:
            raise ValueError(f"Expected exactly one CSV in the source ZIP, found {len(csv_files)}.")

        csv_name = csv_files[0]
        print(f"Reading {csv_name} from ZIP...")

        with zip_file.open(csv_name) as csv_file:
            df = pd.read_csv(csv_file, dtype=str, keep_default_na=False, na_filter=False)

    return df


def load_to_duckdb(df: pd.DataFrame, db_path: Path, table_name: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if table_name != TABLE_NAME:
        raise ValueError(f"Raw loader only supports {TABLE_NAME}.")
    with duckdb.connect(str(db_path)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        con.register("df_view", df)
        con.execute("CREATE OR REPLACE TABLE bronze.raw_severe_injuries AS SELECT * FROM df_view")

    print(f"Loaded {len(df):,} rows into {db_path}, table: {table_name}")


if __name__ == "__main__":
    df = load_csv_from_zip(ZIP_PATH)
    load_to_duckdb(df, DUCKDB_PATH, TABLE_NAME)
