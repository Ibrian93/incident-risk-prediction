from pathlib import Path
import duckdb
import pandas as pd


DUCKDB_PATH = Path("data/processed/safety.duckdb")
REPORTS_TABLES_DIR = Path("reports/tables")


QUERIES = {
    "target_distribution": """
        SELECT
            high_severity_outcome,
            COUNT(*) AS cases,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM fct_injury_cases
        GROUP BY high_severity_outcome
        ORDER BY high_severity_outcome
    """,

    "cases_by_year": """
        SELECT
            event_year,
            COUNT(*) AS cases
        FROM fct_injury_cases
        GROUP BY event_year
        ORDER BY event_year
    """,

    "top_states": """
        SELECT
            state,
            COUNT(*) AS cases
        FROM fct_injury_cases
        WHERE state IS NOT NULL
        GROUP BY state
        ORDER BY cases DESC
        LIMIT 15
    """,

    "top_event_types": """
        SELECT
            event_title,
            COUNT(*) AS cases
        FROM fct_injury_cases
        WHERE event_title IS NOT NULL
        GROUP BY event_title
        ORDER BY cases DESC
        LIMIT 15
    """,

    "top_body_parts": """
        SELECT
            body_part_title,
            COUNT(*) AS cases
        FROM fct_injury_cases
        WHERE body_part_title IS NOT NULL
        GROUP BY body_part_title
        ORDER BY cases DESC
        LIMIT 15
    """,

    "top_sources": """
        SELECT
            source_title,
            COUNT(*) AS cases
        FROM fct_injury_cases
        WHERE source_title IS NOT NULL
        GROUP BY source_title
        ORDER BY cases DESC
        LIMIT 15
    """,

    "high_severity_by_event_type": """
        SELECT
            event_title,
            COUNT(*) AS total_cases,
            SUM(high_severity_outcome) AS high_severity_cases,
            ROUND(100.0 * SUM(high_severity_outcome) / COUNT(*), 2) AS high_severity_rate
        FROM fct_injury_cases
        WHERE event_title IS NOT NULL
        GROUP BY event_title
        HAVING COUNT(*) >= 100
        ORDER BY high_severity_rate DESC
        LIMIT 15
    """,

    "high_severity_by_body_part": """
        SELECT
            body_part_title,
            COUNT(*) AS total_cases,
            SUM(high_severity_outcome) AS high_severity_cases,
            ROUND(100.0 * SUM(high_severity_outcome) / COUNT(*), 2) AS high_severity_rate
        FROM fct_injury_cases
        WHERE body_part_title IS NOT NULL
        GROUP BY body_part_title
        HAVING COUNT(*) >= 100
        ORDER BY high_severity_rate DESC
        LIMIT 15
    """,

    "date_range": """
        SELECT
            MIN(event_date) AS min_event_date,
            MAX(event_date) AS max_event_date,
            COUNT(*) AS total_cases
        FROM fct_injury_cases
    """,
}


def get_missing_values(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    columns = con.execute("DESCRIBE fct_injury_cases").fetchdf()["column_name"].tolist()

    rows = []
    total_rows = con.execute("SELECT COUNT(*) FROM fct_injury_cases").fetchone()[0]

    for column in columns:
        query = f"""
            SELECT COUNT(*) 
            FROM fct_injury_cases 
            WHERE "{column}" IS NULL
        """
        missing_count = con.execute(query).fetchone()[0]
        missing_percentage = round(100.0 * missing_count / total_rows, 2)

        rows.append(
            {
                "column_name": column,
                "missing_count": missing_count,
                "missing_percentage": missing_percentage,
            }
        )

    return pd.DataFrame(rows).sort_values("missing_percentage", ascending=False)


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DUCKDB_PATH}. "
            "Run `python src/load_to_duckdb.py` and `python src/run_sql.py` first."
        )

    REPORTS_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DUCKDB_PATH))

    for name, query in QUERIES.items():
        df = con.execute(query).fetchdf()
        output_path = REPORTS_TABLES_DIR / f"{name}.csv"
        df.to_csv(output_path, index=False)

        print("\n" + "=" * 80)
        print(name.upper())
        print("=" * 80)
        print(df)

    missing_df = get_missing_values(con)
    missing_output_path = REPORTS_TABLES_DIR / "missing_values.csv"
    missing_df.to_csv(missing_output_path, index=False)

    print("\n" + "=" * 80)
    print("MISSING VALUES")
    print("=" * 80)
    print(missing_df)

    con.close()


if __name__ == "__main__":
    main()