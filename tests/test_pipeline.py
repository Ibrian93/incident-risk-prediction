"""Regression checks through the normal acquisition/load/dbt entry point."""
import csv
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = [
    "ID", "UPA", "EventDate", "Employer", "Address1", "Address2", "City", "State",
    "Zip", "Latitude", "Longitude", "Primary NAICS", "Hospitalized", "Amputation",
    "Loss of Eye", "Inspection", "Final Narrative", "Nature", "NatureTitle",
    "Part of Body", "Part of Body Title", "Event", "EventTitle", "Source",
    "SourceTitle", "Secondary Source", "Secondary Source Title", "FederalState",
]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="osha-silver-test-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        for directory in ["src", "config", "osha_injury_ml"]:
            shutil.copytree(
                ROOT / directory, self.root / directory,
                ignore=shutil.ignore_patterns("target", "logs", "__pycache__"),
            )
        self.database = self.root / "data/processed/safety.duckdb"
        self.env = os.environ.copy()
        self.env.update(
            PROJECT_ROOT=str(self.root),
            DUCKDB_PATH=str(self.database),
            DBT_PROFILES_DIR=str(self.root / "config/dbt"),
            SOURCE_ZIP_PATH=str(self.root / "source.zip"),
        )

    def row(self):
        return dict.fromkeys(COLUMNS, "") | {
            "ID": "00001", "EventDate": "01/02/2020", "Employer": " NA ",
            "State": " tx ", "Zip": "00123", "Primary NAICS": "011111",
            "Hospitalized": "1.00", "Loss of Eye": "0.00",
        }

    def source(self, rows):
        text = io.StringIO(newline="")
        writer = csv.DictWriter(text, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        with zipfile.ZipFile(self.root / "source.zip", "w") as source:
            source.writestr("reports.csv", text.getvalue())

    def run_pipeline(self):
        return subprocess.run(
            [sys.executable, str(self.root / "src/run_pipeline.py")],
            cwd=self.root, env=self.env, capture_output=True, text=True,
        )

    def test_raw_fidelity_exact_deduplication_and_repeat_run(self):
        first = self.row()
        later = first | {"EventDate": "01/03/2020"}
        self.source([first, first, later])
        for _ in range(2):
            result = self.run_pipeline()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with duckdb.connect(str(self.database), read_only=True) as con:
                self.assertEqual(
                    con.execute("SELECT count(*) FROM bronze.raw_severe_injuries").fetchone(),
                    (3,),
                )
                self.assertEqual(
                    con.execute("""
                        SELECT "ID", "Employer", "State", "Zip", "Amputation"
                        FROM bronze.raw_severe_injuries LIMIT 1
                    """).fetchone(),
                    ("00001", " NA ", " tx ", "00123", ""),
                )
                self.assertEqual(
                    con.execute("""
                        SELECT count(*), count(amputation_count), min(state),
                               min(zip_code), min(primary_naics), min(employer)
                        FROM silver.stg_severe_injuries
                    """).fetchone(),
                    (2, 0, "TX", "00123", "011111", "NA"),
                )
                self.assertEqual(
                    con.execute("""
                        SELECT count(*) FROM information_schema.tables
                        WHERE table_schema = 'gold'
                    """).fetchone(),
                    (0,),
                )

    def test_conflicting_report_key_fails_without_dropping_records(self):
        first = self.row()
        self.source([first, first | {"Employer": "Different employer"}])
        result = self.run_pipeline()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("assert_unique_incident_id_event_date", result.stdout)
        with duckdb.connect(str(self.database), read_only=True) as con:
            self.assertEqual(
                con.execute("SELECT count(*) FROM silver.stg_severe_injuries").fetchone(),
                (2,),
            )

    def test_malformed_source_numeric_value_fails_validation(self):
        self.source([self.row() | {"Hospitalized": "invalid"}])
        result = self.run_pipeline()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("assert_source_values_parse", result.stdout)


if __name__ == "__main__":
    unittest.main()
