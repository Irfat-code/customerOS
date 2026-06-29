"""
SaaS Support Ticket Generator
Generates realistic support tickets with
severity, status and resolution patterns
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

TICKET_SUBJECTS = [
    'Cannot access dashboard',
    'API integration not working',
    'Data export failing',
    'Billing issue',
    'Performance is slow',
    'Feature request: custom reports',
    'User cannot login',
    'Webhook not firing',
    'Data sync issue',
    'Missing data in reports',
    'Permission settings not saving',
    'SSO configuration help',
]

SEVERITIES = ['low', 'medium', 'high', 'critical']
SEVERITY_WEIGHTS = [0.5, 0.3, 0.15, 0.05]

STATUSES = ['open', 'in_progress', 'resolved', 'closed']


def generate_tickets(
    customers_df: pd.DataFrame,
    days: int = 90
) -> pd.DataFrame:
    """Generate support tickets per customer."""
    tickets = []
    ticket_id = 1
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for _, customer in customers_df.iterrows():
        # Unhealthy customers raise more tickets
        if customer['is_churned']:
            n_tickets = random.randint(3, 15)
        elif customer['segment'] == 'Enterprise':
            n_tickets = random.randint(1, 8)
        else:
            n_tickets = random.randint(0, 5)

        for _ in range(n_tickets):
            created = fake.date_time_between(
                start_date=start_date,
                end_date=end_date
            )
            severity = random.choices(
                SEVERITIES,
                weights=SEVERITY_WEIGHTS
            )[0]

            # Resolution time depends on severity
            resolution_hours = {
                'low': random.randint(24, 168),
                'medium': random.randint(8, 72),
                'high': random.randint(2, 24),
                'critical': random.randint(1, 8),
            }[severity]

            status = random.choices(
                STATUSES,
                weights=[0.1, 0.2, 0.4, 0.3]
            )[0]

            resolved_at = None
            if status in ['resolved', 'closed']:
                resolved_at = (
                    created + timedelta(hours=resolution_hours)
                ).isoformat()

            tickets.append({
                'ticket_id':        f'TKT-{str(ticket_id).zfill(7)}',
                'customer_id':      customer['customer_id'],
                'subject':          random.choice(TICKET_SUBJECTS),
                'severity':         severity,
                'status':           status,
                'resolution_hours': resolution_hours if resolved_at else None,
                'created_at':       created.isoformat(),
                'resolved_at':      resolved_at,
                'updated_at':       datetime.now().isoformat(),
            })
            ticket_id += 1

    return pd.DataFrame(tickets)


if __name__ == '__main__':
    customers = pd.read_csv('data/processed/saas/customers.csv')
    print("Generating support ticket data...")

    tickets = generate_tickets(customers)

    os.makedirs('data/processed/saas', exist_ok=True)
    tickets.to_csv(
        'data/processed/saas/tickets.csv', index=False
    )
    print(f"Tickets: {len(tickets)} records")