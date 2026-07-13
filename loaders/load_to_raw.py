"""
CustomerOS Raw Data Loader
Loads all generated CSV files into PostgreSQL raw database
One table per dataset, one schema per source system
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('.env.local')

# ── Database Connection ──────────────────────────────────────────
def get_engine():
    host     = os.environ.get('RAW_HOST', 'localhost')
    port     = os.environ.get('RAW_PORT', '5435')
    db       = os.environ.get('RAW_DB', 'customeros_raw')
    user     = os.environ.get('RAW_USER', 'raw_user')
    password = os.environ.get('RAW_PASSWORD', 'raw_pass')

    return create_engine(
        f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'
    )


# ── Schema Creation ──────────────────────────────────────────────
def create_schemas(engine):
    schemas = [
        'saas_crm', 'saas_product', 'saas_support',
        'saas_billing', 'saas_nps',
        'fintech_accounts', 'fintech_cards', 'fintech_loans',
        'fintech_transactions', 'observability'
    ]
    with engine.connect() as conn:
        for schema in schemas:
            conn.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS {schema}')
            )
        conn.commit()
    print(f"✓ Created {len(schemas)} schemas")


# ── Load CSV to PostgreSQL ───────────────────────────────────────
def load_csv(
    engine,
    filepath: str,
    schema: str,
    table: str,
    chunk_size: int = 10000
):
    if not os.path.exists(filepath):
        print(f"  ⚠ File not found: {filepath}")
        return 0

    total = 0
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        chunk['_loaded_at'] = datetime.now()
        chunk.to_sql(
            table,
            engine,
            schema=schema,
            if_exists='replace' if total == 0 else 'append',
            index=False,
            method='multi'
        )
        total += len(chunk)

    print(f"  ✓ {schema}.{table}: {total:,} rows")
    return total


# ── PaySim Transaction Loader (sample only) ──────────────────────
def load_paysim_sample(engine, filepath: str, sample_size: int = 100000):
    if not os.path.exists(filepath):
        print(f"  ⚠ PaySim file not found: {filepath}")
        return 0

    print(f"  Loading PaySim sample ({sample_size:,} rows)...")
    df = pd.read_csv(filepath, nrows=sample_size)
    df = df.rename(columns={
        'step':             'step',
        'type':             'transaction_type',
        'amount':           'amount',
        'nameOrig':         'sender_id',
        'oldbalanceOrg':    'sender_old_balance',
        'newbalanceOrig':   'sender_new_balance',
        'nameDest':         'receiver_id',
        'oldbalanceDest':   'receiver_old_balance',
        'newbalanceDest':   'receiver_new_balance',
        'isFraud':          'is_fraud',
        'isFlaggedFraud':   'is_flagged_fraud',
    })
    df['transaction_id'] = [
        f'TXN-{str(i+1).zfill(10)}' for i in range(len(df))
    ]
    df['_loaded_at'] = datetime.now()

    df.to_sql(
        'transactions',
        engine,
        schema='fintech_transactions',
        if_exists='replace',
        index=False,
        method='multi',
        chunksize=5000
    )
    print(f"  ✓ fintech_transactions.transactions: {len(df):,} rows")
    return len(df)


# ── Main Loader ──────────────────────────────────────────────────
def run_loader():
    print("\n" + "="*50)
    print("CustomerOS Raw Data Loader")
    print("="*50)

    engine = get_engine()
    create_schemas(engine)

    base = 'data/processed'

    print("\n[SaaS] Loading CRM data...")
    load_csv(engine, f'{base}/saas/customers.csv',
             'saas_crm', 'customers')
    load_csv(engine, f'{base}/saas/accounts.csv',
             'saas_crm', 'accounts')
    load_csv(engine, f'{base}/saas/contacts.csv',
             'saas_crm', 'contacts')

    print("\n[SaaS] Loading product usage...")
    load_csv(engine, f'{base}/saas/sessions.csv',
             'saas_product', 'sessions')
    load_csv(engine, f'{base}/saas/feature_usage.csv',
             'saas_product', 'feature_usage')

    print("\n[SaaS] Loading support data...")
    load_csv(engine, f'{base}/saas/tickets.csv',
             'saas_support', 'tickets')

    print("\n[SaaS] Loading billing data...")
    load_csv(engine, f'{base}/saas/invoices.csv',
             'saas_billing', 'invoices')
    load_csv(engine, f'{base}/saas/payments.csv',
             'saas_billing', 'payments')

    print("\n[SaaS] Loading NPS data...")
    load_csv(engine, f'{base}/saas/nps_responses.csv',
             'saas_nps', 'responses')

    print("\n[Fintech] Loading account data...")
    load_csv(engine, f'{base}/fintech/customers.csv',
             'fintech_accounts', 'customers')
    load_csv(engine, f'{base}/fintech/accounts.csv',
             'fintech_accounts', 'accounts')

    print("\n[Fintech] Loading cards...")
    load_csv(engine, f'{base}/fintech/cards.csv',
             'fintech_cards', 'cards')

    print("\n[Fintech] Loading loans...")
    load_csv(engine, f'{base}/fintech/loans.csv',
             'fintech_loans', 'loans')
    load_csv(engine, f'{base}/fintech/repayments.csv',
             'fintech_loans', 'repayments')

    print("\n[Fintech] Loading transactions (PaySim sample)...")
    load_paysim_sample(
        engine,
        'data/raw/fintech/PS_20174392719_1491204439457_log.csv',
        sample_size=100000
    )

    print("\n" + "="*50)
    print("✅ All data loaded into PostgreSQL!")
    print("="*50 + "\n")


if __name__ == '__main__':
    run_loader()