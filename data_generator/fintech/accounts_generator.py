"""
Fintech Accounts Generator
Generates customer accounts and KYC records
Links to PaySim transaction data
"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker()
Faker.seed(42)
random.seed(42)

COUNTRIES = [
    'Nigeria', 'Kenya', 'Ghana', 'South Africa',
    'United Kingdom', 'United States', 'Canada',
    'Germany', 'France', 'India'
]

ACCOUNT_TYPES = ['savings', 'current', 'business', 'premium']
SEGMENTS = ['retail', 'sme', 'corporate', 'premium']
KYC_STATUSES = ['verified', 'pending', 'failed', 'expired']


def generate_customers(n: int = 2000) -> pd.DataFrame:
    """Generate fintech customer records."""
    customers = []

    for i in range(n):
        created_at = fake.date_time_between(
            start_date='-3y', end_date='-1m'
        )
        segment = random.choices(
            SEGMENTS,
            weights=[0.5, 0.25, 0.15, 0.1]
        )[0]

        customers.append({
            'customer_id':  f'FIN-{str(i+1).zfill(6)}',
            'first_name':   fake.first_name(),
            'last_name':    fake.last_name(),
            'email':        fake.email(),
            'phone':        fake.phone_number(),
            'country':      random.choice(COUNTRIES),
            'segment':      segment,
            'kyc_status':   random.choices(
                KYC_STATUSES,
                weights=[0.75, 0.1, 0.05, 0.1]
            )[0],
            'is_active':    random.random() > 0.1,
            'created_at':   created_at.isoformat(),
            'updated_at':   datetime.now().isoformat(),
        })

    return pd.DataFrame(customers)


def generate_accounts(
    customers_df: pd.DataFrame
) -> pd.DataFrame:
    """Generate bank accounts per customer."""
    accounts = []
    account_id = 1

    for _, customer in customers_df.iterrows():
        n_accounts = random.choices(
            [1, 2, 3],
            weights=[0.6, 0.3, 0.1]
        )[0]

        for _ in range(n_accounts):
            created_at = datetime.fromisoformat(customer["created_at"])

            opened_at = fake.date_time_between(
            start_date=created_at,
            end_date="now"
            )
            account_type = random.choice(ACCOUNT_TYPES)
            balance = round(random.uniform(0, 50000), 2)

            accounts.append({
                'account_id':   f'ACC-{str(account_id).zfill(8)}',
                'customer_id':  customer['customer_id'],
                'account_type': account_type,
                'balance':      balance,
                'currency':     'USD',
                'status':       random.choices(
                    ['active', 'dormant', 'closed', 'frozen'],
                    weights=[0.7, 0.15, 0.1, 0.05]
                )[0],
                'opened_at':    opened_at.isoformat(),
                'created_at':   opened_at.isoformat(),
                'updated_at':   datetime.now().isoformat(),
            })
            account_id += 1

    return pd.DataFrame(accounts)


if __name__ == '__main__':
    print("Generating fintech account data...")
    customers = generate_customers(2000)
    accounts = generate_accounts(customers)

    os.makedirs('data/processed/fintech', exist_ok=True)
    customers.to_csv(
        'data/processed/fintech/customers.csv', index=False
    )
    accounts.to_csv(
        'data/processed/fintech/accounts.csv', index=False
    )

    print(f"Customers: {len(customers)} records")
    print(f"Accounts:  {len(accounts)} records")