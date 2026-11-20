# Data Engineering decisions

## Scope

The current goal is a Docker-executable medallion foundation through silver.
The source provides a ZIP containing a CSV. API ingestion and gold outputs need
separate requirements.

## Raw / bronze fidelity

Pandas type inference previously converted source fields during ingestion.
The loader now reads every field as text and disables automatic NA recognition.
This preserves leading zeros, empty strings, literal NA-like text and whitespace.
The original ZIP preserves the source bytes.

The database is a current snapshot, refreshed in full. Immutable historical
snapshots and source revision tracking are future improvements.

## Silver cleaning

Silver owns naming, whitespace cleanup, missing-value representation and type
conversion. Source outcome counts remain source attributes. Missing counts are
not inferred as zero, and no severity target is derived.

Materializing silver as a table makes its build and validation explicit.
Consumers must check that the whole pipeline completed successfully.

## Duplicate policy

Exact source duplicate rows can be removed. Repeated source IDs can represent
different valid reports, so deduplicating by ID alone would lose data.

The incident/date combination is tested against the current snapshot.
Conflicting keys stop validation and require review. The pipeline does not
arbitrarily choose one record.

## Runtime

Docker defines the Python environment. Compose manages a persistent data volume
and mounts the supplied snapshot read-only. This avoids depending on automated
OSHA download availability during a reproducible run.

Airflow remains an optional orchestration entry point. The batch runner provides
the default execution path.

## Browser exploration

The optional DuckDB UI service uses a read-only attachment to the pipeline
database. UI metadata has its own writable catalog and volume. A TCP forwarder
exposes the extension's loopback listener through a localhost-only published port
in Docker Desktop. The pipeline and viewer must use the same Compose project.

Stop the viewer before a write run, then restart it to release and reacquire the
database attachment. This respects DuckDB's cross-process locking.
