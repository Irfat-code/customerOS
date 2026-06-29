"""
SaaS CRM Generator
Generates realistic SaaS customers, accounts and contacts
Enriches the Kaggle customer segmentation dataset
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
np.random.seed(42)

# SaaS plan configuration
PLANS = {
    'starter':    {'mrr': (29, 99),    'segment': 'SMB'},
    'growth':     {'mrr': (99, 499),   'segment': 'SMB'},
    'business':   {'mrr': (499, 1999), 'segment': 'Mid-Market'},
    'enterprise': {'mrr': (1999, 9999),'segment': 'Enterprise'},
}

INDUSTRIES = [
    'SaaS', 'Fintech', 'Healthcare', 'E-commerce',
    'Education', 'Real Estate', 'Marketing', 'Legal',
    'Manufacturing', 'Consulting'
]

COUNTRIES = [
    'United States', 'United Kingdom', 'Canada', 'Australia',
    'Germany', 'France', 'Netherlands', 'Singapore',
    'Nigeria', 'South Africa', 'Kenya', 'India'
]


def generate_customers(n: int = 1000) -> pd.DataFrame:
    """Generate SaaS customer records."""
    customers = []

    for i in range(n):
        plan = random.choice(list(PLANS.keys()))
        plan_config = PLANS[plan]
        mrr = round(random.uniform(*plan_config['mrr']), 2)
        start_date = fake.date_between(
            start_date='-3y', end_date='-1m'
        )
        is_churned = random.random() < 0.15  # 15% churn rate

        customers.append({
            'customer_id':      f'CUST-{str(i+1).zfill(5)}',
            'company_name':     fake.company(),
            'email':            fake.company_email(),
            'industry':         random.choice(INDUSTRIES),
            'country':          random.choice(COUNTRIES),
            'plan':             plan,
            'segment':          plan_config['segment'],
            'mrr':              mrr,
            'arr':              round(mrr * 12, 2),
            'customer_since':   start_date.isoformat(),
            'is_churned':       is_churned,
            'churned_at':       (
                start_date + timedelta(
                    days=random.randint(30, 900)
                )
            ).isoformat() if is_churned else None,
            'created_at':       start_date.isoformat(),
            'updated_at':       datetime.now().isoformat(),
        })

    return pd.DataFrame(customers)


def generate_accounts(customers_df: pd.DataFrame) -> pd.DataFrame:
    """Generate account details linked to customers."""
    accounts = []

    for _, customer in customers_df.iterrows():
        contract_value = customer['arr']
        start_date = customer['customer_since']

        accounts.append({
            'account_id':       f'ACC-{customer["customer_id"]}',
            'customer_id':      customer['customer_id'],
            'plan':             customer['plan'],
            'contract_value':   contract_value,
            'billing_cycle':    random.choice(['monthly', 'annual']),
            'start_date':       start_date,
            'renewal_date':     (
                datetime.fromisoformat(start_date) +
                timedelta(days=365)
            ).isoformat(),
            'auto_renew':       random.choice([True, False]),
            'created_at':       start_date,
            'updated_at':       datetime.now().isoformat(),
        })

    return pd.DataFrame(accounts)


def generate_contacts(customers_df: pd.DataFrame) -> pd.DataFrame:
    """Generate contacts (decision makers) per account."""
    contacts = []
    contact_id = 1

    for _, customer in customers_df.iterrows():
        n_contacts = random.randint(1, 4)
        roles = [
            'CEO', 'CTO', 'VP Engineering',
            'Head of Data', 'Engineering Manager',
            'Data Engineer', 'Analytics Lead'
        ]

        for j in range(n_contacts):
            contacts.append({
                'contact_id':       f'CON-{str(contact_id).zfill(6)}',
                'customer_id':      customer['customer_id'],
                'first_name':       fake.first_name(),
                'last_name':        fake.last_name(),
                'email':            fake.email(),
                'role':             random.choice(roles),
                'is_primary':       j == 0,
                'created_at':       customer['customer_since'],
                'updated_at':       datetime.now().isoformat(),
            })
            contact_id += 1

    return pd.DataFrame(contacts)


if __name__ == '__main__':
    print("Generating SaaS CRM data...")
    customers = generate_customers(1000)
    accounts = generate_accounts(customers)
    contacts = generate_contacts(customers)

    os.makedirs('data/processed/saas', exist_ok=True)
    customers.to_csv('data/processed/saas/customers.csv', index=False)
    accounts.to_csv('data/processed/saas/accounts.csv', index=False)
    contacts.to_csv('data/processed/saas/contacts.csv', index=False)

    print(f"Customers: {len(customers)} records")
    print(f"Accounts:  {len(accounts)} records")
    print(f"Contacts:  {len(contacts)} records")