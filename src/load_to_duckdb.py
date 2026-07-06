from pathlib import Path
import zipfile
import pandas as pd
import duckdb

ZIP_PATH = Path("data/raw/osha_severe_injuries.zip")
DUCKDB_PATH = Path("data/processed/safety.duckdb")
TABLE_NAME = "raw_severe_injuries"


def load_csv_from_zip(zip_path: Path) -> pd.DataFrame:
    if not zip_path.exists():
        raise FileNotFoundError(f"Missing file: {zip_path}. Run `python src/download_data.py` first.")
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        csv_files = [name for name in zip_file.namelist() if name.endswith(".csv")]

        if not csv_files:
            raise ValueError("No CSV file found inside the ZIP.")

        csv_name = csv_files[0]
        print(f"Reading {csv_name} from ZIP...")

        with zip_file.open(csv_name) as csv_file:
            df = pd.read_csv(csv_file, low_memory=False)

    return df


def load_to_duckdb(df: pd.DataFrame, db_path: Path, table_name: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))
    con.register("df_view", df)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} as SELECT * FROM df_view")
    con.close()

    print(f"Loaded {len(df):,} rows into {db_path}, table: {table_name}")


if __name__ == "__main__":
    df = load_csv_from_zip(ZIP_PATH)
    load_to_duckdb(df, DUCKDB_PATH, TABLE_NAME)
