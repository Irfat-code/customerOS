"""
SaaS Product Usage Generator
Generates realistic product usage data including
sessions, feature usage and API calls
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

FEATURES = [
    'dashboard', 'reports', 'analytics', 'api_access',
    'data_export', 'team_management', 'integrations',
    'alerts', 'custom_dashboards', 'data_import',
    'scheduling', 'collaboration', 'audit_logs'
]


def generate_sessions(
    customers_df: pd.DataFrame,
    days: int = 90
) -> pd.DataFrame:
    """Generate daily session data per customer."""
    sessions = []
    session_id = 1
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for _, customer in customers_df.iterrows():
        if customer['is_churned']:
            # Churned customers have declining sessions
            base_sessions = random.randint(0, 2)
        elif customer['segment'] == 'Enterprise':
            base_sessions = random.randint(5, 20)
        elif customer['segment'] == 'Mid-Market':
            base_sessions = random.randint(2, 10)
        else:
            base_sessions = random.randint(0, 5)

        current_date = start_date
        while current_date <= end_date:
            # Weekends have fewer sessions
            if current_date.weekday() >= 5:
                day_sessions = max(
                    0, base_sessions - random.randint(2, 4)
                )
            else:
                day_sessions = max(
                    0,
                    base_sessions + random.randint(-2, 2)
                )

            for _ in range(day_sessions):
                sessions.append({
                    'session_id':       f'SES-{str(session_id).zfill(8)}',
                    'customer_id':      customer['customer_id'],
                    'session_date':     current_date.date().isoformat(),
                    'duration_mins':    round(
                        random.uniform(2, 120), 1
                    ),
                    'device':           random.choice(
                        ['desktop', 'mobile', 'tablet']
                    ),
                    'created_at':       current_date.isoformat(),
                })
                session_id += 1

            current_date += timedelta(days=1)

    return pd.DataFrame(sessions)


def generate_feature_usage(
    customers_df: pd.DataFrame,
    days: int = 90
) -> pd.DataFrame:
    """Generate feature usage data per customer."""
    usage = []
    usage_id = 1
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for _, customer in customers_df.iterrows():
        # Enterprise customers use more features
        if customer['segment'] == 'Enterprise':
            n_features = random.randint(7, 13)
        elif customer['segment'] == 'Mid-Market':
            n_features = random.randint(4, 9)
        else:
            n_features = random.randint(1, 6)

        customer_features = random.sample(FEATURES, n_features)

        for feature in customer_features:
            current_date = start_date
            while current_date <= end_date:
                if random.random() < 0.6:  # 60% chance of use per day
                    usage.append({
                        'usage_id':     f'USG-{str(usage_id).zfill(8)}',
                        'customer_id':  customer['customer_id'],
                        'feature_name': feature,
                        'usage_count':  random.randint(1, 50),
                        'usage_date':   current_date.date().isoformat(),
                        'created_at':   current_date.isoformat(),
                    })
                    usage_id += 1
                current_date += timedelta(days=1)

    return pd.DataFrame(usage)


if __name__ == '__main__':
    customers = pd.read_csv('data/processed/saas/customers.csv')
    print("Generating product usage data...")

    sessions = generate_sessions(customers)
    feature_usage = generate_feature_usage(customers)

    os.makedirs('data/processed/saas', exist_ok=True)
    sessions.to_csv(
        'data/processed/saas/sessions.csv', index=False
    )
    feature_usage.to_csv(
        'data/processed/saas/feature_usage.csv', index=False
    )

    print(f"Sessions:      {len(sessions)} records")
    print(f"Feature usage: {len(feature_usage)} records")