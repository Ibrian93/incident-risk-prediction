# OSHA bronze source and silver transformations

The existing dbt project/profile name is retained for configuration compatibility.
This project registers `bronze.raw_severe_injuries` and builds
`silver.stg_severe_injuries` as a table.

Run acquisition and bronze loading first with the repository pipeline.

```bash
docker compose run --rm pipeline
```

To rebuild and test silver after bronze already exists, run from the repository
root.

```bash
docker compose run --rm pipeline dbt build --project-dir osha_injury_ml
```

The image configures `DBT_PROFILES_DIR` and `DUCKDB_PATH`. Direct local dbt
execution must supply these environment variables explicitly.

See the root README for raw fidelity, cleaning rules, duplicate policy, persistence
and development commands.
