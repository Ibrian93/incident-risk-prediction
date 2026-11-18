"""Inspect the bronze and silver datasets without modifying the database."""
import duckdb

from config import DUCKDB_PATH


def main() -> None:
    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as con:
        for relation in ["bronze.raw_severe_injuries", "silver.stg_severe_injuries"]:
            print(f"\n{relation}")
            print(con.execute(f"SELECT COUNT(*) AS rows FROM {relation}").fetchdf())
            print(con.execute(f"DESCRIBE {relation}").fetchdf())
        print(con.execute("""
            SELECT MIN(event_date) AS first_event, MAX(event_date) AS last_event,
                   COUNT(DISTINCT state) AS states
            FROM silver.stg_severe_injuries
        """).fetchdf())


if __name__ == "__main__":
    main()
