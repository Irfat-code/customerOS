# CustomerOS Pipeline DAG

Orchestrates the full data pipeline from raw CSV/PaySim ingestion through
to validated Customer 360 models.

## Tasks (sequential)
1. **load_raw_data** — loads SaaS + fintech CSVs and a PaySim fraud sample
   into `raw_db`, one schema per source system. Idempotent: truncates
   existing tables before reloading rather than dropping them, so it can
   be re-run safely without breaking dbt views/tables built on top.
2. **dbt_run_staging** — casts raw text columns to proper types, renames
   for consistency, one clean view per source table.
3. **dbt_run_intelligence** — builds per-pillar signal models (engagement,
   commercial, support, sentiment for SaaS; activity, repayment, compliance
   for fintech).
4. **dbt_run_customer_360** — combines intelligence pillars into a single
   composite health/risk score per customer, validated against real
   outcomes (is_churned for SaaS, has_repayment_problem for fintech).
5. **dbt_test_all** — runs all dbt tests (uniqueness, not-null, referential
   integrity, accepted values) across every layer.

## Running
Trigger manually from the Airflow UI (http://localhost:8080) or:
\`\`\`
docker exec customeros-airflow-scheduler-1 airflow dags trigger customer_os_pipeline
\`\`\`

Currently unscheduled (`schedule_interval=None`) since source data is
static/generated rather than live. Change to `@daily` or similar once
connected to a periodically-refreshed source.