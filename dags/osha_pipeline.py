from airflow.sdk import DAG, task
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="osha_pipeline",
    start_date=datetime(2026, 8, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    run_extract_and_load_raw = BashOperator(
        task_id="run_extract_and_load_raw",
        bash_command="""
        cd /home/ibrian93/incident-risk-prediction/osha_injury_ml &&
        python src/download_data.py 
        """
    )
    
    run_staging = BashOperator(
        task_id="run_staging",
        bash_command="""
        cd /home/ibrian93/incident-risk-prediction/osha_injury_ml &&
        dbt run --select stg_severe_injuries
        """
    )
    
    run_extract_and_load_raw >> run_staging
    
     