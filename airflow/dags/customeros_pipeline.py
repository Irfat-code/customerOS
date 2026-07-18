"""
CustomerOS Pipeline DAG
Orchestrates: raw load -> staging -> intelligence -> customer_360 -> tests

Runs inside the Airflow scheduler container, which already has dbt-core
and the loader dependencies installed (see Dockerfile.airflow). No docker
exec needed - these tasks run directly in this container's environment.
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/airflow/dbt_customeros"
DBT_PROFILES_DIR = "/opt/airflow/dbt_customeros"

default_args = {
    "owner": "customeros",
    "retries": 1,
}

with DAG(
    dag_id="customer_os_pipeline",
    description="Load raw data, build staging/intelligence/customer_360 layers, run tests",
    default_args=default_args,
    schedule_interval=None,  # manual trigger for now; set a cron later if needed
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["customeros", "dbt"],
) as dag:

    load_raw_data = BashOperator(
        task_id="load_raw_data",
        bash_command="python /opt/airflow/loaders/load_to_raw.py",
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=(
            f"dbt run --select staging "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_run_intelligence = BashOperator(
        task_id="dbt_run_intelligence",
        bash_command=(
            f"dbt run --select intelligence "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_run_customer_360 = BashOperator(
        task_id="dbt_run_customer_360",
        bash_command=(
            f"dbt run --select customer_360 "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_test_all = BashOperator(
        task_id="dbt_test_all",
        bash_command=(
            f"dbt test "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )
    dbt_source_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=(
            f"dbt source freshness "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=(
            f"dbt snapshot "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_run_observability = BashOperator(
        task_id="dbt_run_observability",
        bash_command=(
            f"dbt run --select observability "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    load_raw_data >> [dbt_source_freshness, dbt_run_staging, dbt_snapshot]
    dbt_run_staging >> dbt_run_intelligence >> dbt_run_customer_360
    [dbt_run_intelligence, dbt_snapshot] >> dbt_run_observability
    [dbt_run_customer_360, dbt_run_observability] >> dbt_test_all