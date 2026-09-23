from pathlib import Path
import duckdb


DUCKDB_PATH = Path("data/processed/safety.duckdb")


QUERIES = {
    "row_count": """
        SELECT COUNT(*) AS rows
        FROM fct_injury_cases
    """,

    "target_distribution": """
        SELECT 
            high_severity_outcome,
            COUNT(*) AS cases
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
        GROUP BY state
        ORDER BY cases DESC
        LIMIT 10
    """,
}


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DUCKDB_PATH}. "
            "Run `python src/load_to_duckdb.py` first."
        )

    con = duckdb.connect(str(DUCKDB_PATH))

    for name, query in QUERIES.items():
        print("\n" + "=" * 80)
        print(name.upper())
        print("=" * 80)
        print(con.execute(query).fetchdf())

    con.close()


if __name__ == "__main__":
    main()