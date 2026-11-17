FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
ENV PROJECT_ROOT=/opt/project
ENV DUCKDB_PATH=/opt/project/data/processed/safety.duckdb
ENV DBT_PROFILES_DIR=/opt/project/config/dbt

WORKDIR /opt/project
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt
COPY src/ src/
COPY osha_injury_ml/ osha_injury_ml/
COPY config/dbt/ config/dbt/
RUN mkdir -p data/raw data/processed
CMD ["python", "src/run_pipeline.py"]


FROM runtime AS pipeline
