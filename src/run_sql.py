from pathlib import Path
import duckdb


DUCKDB_PATH = Path("data/processed/safety.duckdb")

SQL_FILES = [
    Path("sql/01_raw_to_staging.sql"),
    Path("sql/02_feature_table.sql"),
]


def run_sql_file(con: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    sql = sql_path.read_text()
    con.execute(sql)
    print(f"Executed {sql_path}")


if __name__ == "__main__":
    con = duckdb.connect(str(DUCKDB_PATH))

    for sql_file in SQL_FILES:
        run_sql_file(con, sql_file)

    con.close()