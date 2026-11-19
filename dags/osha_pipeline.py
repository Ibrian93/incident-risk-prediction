"""Portable Airflow DAG. Tasks need the project runtime installed on the worker."""
import os
from datetime import datetime
from pathlib import Path

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parents[1]))
TASK_ENV = {
    "PROJECT_ROOT": str(PROJECT_ROOT),
    "DUCKDB_PATH": os.environ.get(
        "DUCKDB_PATH", str(PROJECT_ROOT / "data/processed/safety.duckdb")
    ),
    "DBT_PROFILES_DIR": os.environ.get(
        "DBT_PROFILES_DIR", str(PROJECT_ROOT / "config/dbt")
    ),
}

with DAG(
    dag_id="osha_pipeline",
    start_date=datetime(2026, 8, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
) as dag:
    download = BashOperator(
        task_id="download",
        cwd=str(PROJECT_ROOT),
        env=TASK_ENV,
        append_env=True,
        bash_command="python src/download_data.py",
    )
    load_raw = BashOperator(
        task_id="load_raw",
        cwd=str(PROJECT_ROOT),
        env=TASK_ENV,
        append_env=True,
        bash_command="python src/load_to_duckdb.py",
    )
    build_silver = BashOperator(
        task_id="build_silver",
        cwd=str(PROJECT_ROOT),
        env=TASK_ENV,
        append_env=True,
        bash_command="dbt build --project-dir osha_injury_ml",
    )

    download >> load_raw >> build_silver
