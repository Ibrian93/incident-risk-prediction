from pathlib import Path
import duckdb

DUCKDB_PATH = Path("data/processed/safety.duckdb")

def main() -> None:
    con = duckdb.connect(str(DUCKDB_PATH))

    print("\nRow count:")
    print(con.execute("SELECT COUNT(*) FROM raw_severe_injuries").fetchdf())

    print("\nSchema:")
    print(con.execute("DESCRIBE raw_severe_injuries").fetchdf())

    print("\nSample rows:")
    print(con.execute("SELECT * FROM raw_severe_injuries LIMIT 5").fetchdf())


    print("\nDate range:")
    print(con.execute(
        """
        SELECT 
            MIN(TRY_CAST(EventDate AS DATE)) AS min_event_date,
            MAX(TRY_CAST(EventDate AS DATE)) AS max_event_date
        FROM raw_severe_injuries
        """
    ).fetchdf())

    print("\nOutcome counts")
    print(
            con.execute(
                """
                SELECT
                    SUM(COALESCE(Hospitalized, 0)) AS total_hospitalized,
                    SUM(COALESCE(Amputation, 0)) AS total_amputations,
                    SUM(COALESCE("Loss of Eye", 0)) AS total_loss_of_eye
                FROM raw_severe_injuries
                """
                ).fetchdf()
            )

    con.close()

if __name__ == "__main__":
    main()
