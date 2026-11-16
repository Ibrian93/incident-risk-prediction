"""Acquire the source, load bronze, and build and test silver."""
import os
import subprocess
import sys

from config import DBT_PROFILES_DIR, DUCKDB_PATH, PROJECT_ROOT


def main() -> None:
    env = os.environ.copy()
    env["DUCKDB_PATH"] = str(DUCKDB_PATH)
    env["DBT_PROFILES_DIR"] = str(DBT_PROFILES_DIR)
    commands = [
        [sys.executable, str(PROJECT_ROOT / "src/download_data.py")],
        [sys.executable, str(PROJECT_ROOT / "src/load_to_duckdb.py")],
        [sys.executable, "-c", "from dbt.cli.main import cli; cli()", "build",
         "--project-dir", str(PROJECT_ROOT / "osha_injury_ml")],
    ]
    for command in commands:
        print("Running " + " ".join(command), flush=True)
        subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
