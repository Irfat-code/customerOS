"""
CustomerOS Project Audit
Run from project root: python project_audit.py

Checks:
  1. Git state
  2. Expected folder/file structure
  3. Docker containers
  4. Postgres raw_db: schemas, tables, row counts
  5. Postgres warehouse_db: schemas, tables
  6. dbt project presence
  7. Airflow DAGs
"""
import os
import subprocess
import sys

ROOT = os.getcwd()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def run(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return f"[error running command] {e}"


# ── 1. Git state ──────────────────────────────────────────────
section("1. GIT STATE")
print(run("git status --short"))
print("\nLast 5 commits:")
print(run('git log --oneline -5'))
print("\nIs data/processed ignored?")
print(run("git check-ignore -v data/processed/saas/customers.csv"))


# ── 2. Folder / file structure ──────────────────────────────────
section("2. EXPECTED FILES / FOLDERS")
expected = [
    "docker-compose.yml",
    "Dockerfile.airflow",
    ".gitignore",
    ".env",
    "loaders/requirements.txt",
    "loaders/load_to_raw.py",
    "data/processed/saas",
    "data/processed/fintech",
    "data/raw/fintech",
    "dbt",              # dbt project dir, if created yet
    "dags",             # airflow dags folder
]
for path in expected:
    full = os.path.join(ROOT, path)
    status = "FOUND" if os.path.exists(full) else "MISSING"
    print(f"  [{status:7}] {path}")


# ── 3. Docker containers ────────────────────────────────────────
section("3. DOCKER CONTAINERS")
print(run("docker compose ps"))
print("\nImages:")
print(run("docker images --filter reference=customeros*"))


# ── 4. Postgres raw_db contents ─────────────────────────────────
section("4. POSTGRES raw_db (schemas / tables / row counts)")
try:
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    load_dotenv()

    host = os.environ.get("RAW_HOST", "localhost")
    port = os.environ.get("RAW_PORT", "5435")
    db = os.environ.get("RAW_DB", "customeros_raw")
    user = os.environ.get("RAW_USER", "raw_user")
    password = os.environ.get("RAW_PASSWORD", "raw_pass")

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

    with engine.connect() as conn:
        schemas = conn.execute(text("""
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog','information_schema','public')
            ORDER BY schema_name
        """)).fetchall()

        if not schemas:
            print("  No custom schemas found yet — loader hasn't run successfully.")
        for (schema,) in schemas:
            tables = conn.execute(text(f"""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = '{schema}'
            """)).fetchall()
            print(f"\n  schema: {schema}")
            if not tables:
                print("    (no tables)")
            for (table,) in tables:
                try:
                    count = conn.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')).scalar()
                    print(f"    {table}: {count:,} rows")
                except Exception as e:
                    print(f"    {table}: [error counting rows: {e}]")

except ImportError:
    print("  sqlalchemy/psycopg2/python-dotenv not installed locally.")
    print("  Run: pip install sqlalchemy psycopg2-binary python-dotenv")
except Exception as e:
    print(f"  Could not connect to raw_db: {e}")
    print("  Check: is the raw_db container running? Is the port 5435 correct?")


# ── 5. Postgres warehouse_db ────────────────────────────────────
section("5. POSTGRES warehouse_db (schemas / tables)")
try:
    from sqlalchemy import create_engine, text
    wh_host = os.environ.get("WAREHOUSE_HOST", "localhost")
    wh_port = os.environ.get("WAREHOUSE_PORT", "5436")
    wh_db = os.environ.get("WAREHOUSE_DB", "customeros_warehouse")
    wh_user = os.environ.get("WAREHOUSE_USER", "warehouse_user")
    wh_password = os.environ.get("WAREHOUSE_PASSWORD", "warehouse_pass")

    wh_engine = create_engine(
        f"postgresql+psycopg2://{wh_user}:{wh_password}@{wh_host}:{wh_port}/{wh_db}"
    )
    with wh_engine.connect() as conn:
        schemas = conn.execute(text("""
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog','information_schema','public')
            ORDER BY schema_name
        """)).fetchall()
        if not schemas:
            print("  No custom schemas yet — expected at this stage (dbt not run yet).")
        for (schema,) in schemas:
            print(f"  schema: {schema}")
except Exception as e:
    print(f"  Could not connect to warehouse_db (may not be needed yet): {e}")


# ── 6. dbt project ───────────────────────────────────────────────
section("6. DBT PROJECT")
dbt_project_file = os.path.join(ROOT, "dbt_project.yml")
if os.path.exists(dbt_project_file) or os.path.exists(os.path.join(ROOT, "dbt", "dbt_project.yml")):
    print("  dbt project scaffolding found.")
else:
    print("  No dbt_project.yml found yet — dbt modeling hasn't started.")

# ── 7. Airflow DAGs ──────────────────────────────────────────────
section("7. AIRFLOW DAGS")
dag_dir = os.path.join(ROOT, "dags")
if os.path.isdir(dag_dir):
    dag_files = [f for f in os.listdir(dag_dir) if f.endswith(".py")]
    if dag_files:
        print(f"  {len(dag_files)} DAG file(s) found:")
        for f in dag_files:
            print(f"    - {f}")
    else:
        print("  dags/ folder exists but is empty — no DAGs written yet.")
else:
    print("  No dags/ folder found yet.")

section("AUDIT COMPLETE")
print("Paste this full output back to continue from an accurate baseline.\n")