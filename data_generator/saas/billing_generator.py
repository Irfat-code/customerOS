"""
SaaS Billing Generator
Generates invoices and payment records
including failures and overdue patterns
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

PAYMENT_METHODS = [
    'credit_card', 'bank_transfer',
    'paypal', 'stripe'
]


def generate_invoices(
    customers_df: pd.DataFrame
) -> pd.DataFrame:
    """Generate monthly invoices per customer."""
    invoices = []
    invoice_id = 1

    for _, customer in customers_df.iterrows():
        start = datetime.fromisoformat(customer['customer_since'])
        months_active = max(
            1,
            (datetime.now() - start).days // 30
        )

        for month in range(months_active):
            invoice_date = start + timedelta(days=30 * month)
            due_date = invoice_date + timedelta(days=30)

            # Churned customers have more overdue invoices
            if customer['is_churned'] and month > months_active - 3:
                status = random.choices(
                    ['paid', 'overdue', 'failed'],
                    weights=[0.3, 0.4, 0.3]
                )[0]
            else:
                status = random.choices(
                    ['paid', 'overdue', 'failed'],
                    weights=[0.85, 0.1, 0.05]
                )[0]

            invoices.append({
                'invoice_id':   f'INV-{str(invoice_id).zfill(8)}',
                'customer_id':  customer['customer_id'],
                'amount':       customer['mrr'],
                'currency':     'USD',
                'status':       status,
                'invoice_date': invoice_date.date().isoformat(),
                'due_date':     due_date.date().isoformat(),
                'created_at':   invoice_date.isoformat(),
                'updated_at':   datetime.now().isoformat(),
            })
            invoice_id += 1

    return pd.DataFrame(invoices)


def generate_payments(
    invoices_df: pd.DataFrame
) -> pd.DataFrame:
    """Generate payment records for paid invoices."""
    payments = []
    payment_id = 1

    for _, invoice in invoices_df.iterrows():
        if invoice['status'] == 'paid':
            paid_at = (
                datetime.fromisoformat(invoice['invoice_date']) +
                timedelta(days=random.randint(0, 15))
            )

            payments.append({
                'payment_id':   f'PAY-{str(payment_id).zfill(8)}',
                'invoice_id':   invoice['invoice_id'],
                'customer_id':  invoice['customer_id'],
                'amount_paid':  invoice['amount'],
                'currency':     'USD',
                'method':       random.choice(PAYMENT_METHODS),
                'status':       'success',
                'paid_at':      paid_at.isoformat(),
                'created_at':   paid_at.isoformat(),
            })
            payment_id += 1

        elif invoice['status'] == 'failed':
            # Failed payment attempt
            attempted_at = (
                datetime.fromisoformat(invoice['invoice_date']) +
                timedelta(days=random.randint(0, 5))
            )
            payments.append({
                'payment_id':   f'PAY-{str(payment_id).zfill(8)}',
                'invoice_id':   invoice['invoice_id'],
                'customer_id':  invoice['customer_id'],
                'amount_paid':  0,
                'currency':     'USD',
                'method':       random.choice(PAYMENT_METHODS),
                'status':       'failed',
                'paid_at':      None,
                'created_at':   attempted_at.isoformat(),
            })
            payment_id += 1

    return pd.DataFrame(payments)


if __name__ == '__main__':
    customers = pd.read_csv('data/processed/saas/customers.csv')
    print("Generating billing data...")

    invoices = generate_invoices(customers)
    payments = generate_payments(invoices)

    os.makedirs('data/processed/saas', exist_ok=True)
    invoices.to_csv(
        'data/processed/saas/invoices.csv', index=False
    )
    payments.to_csv(
        'data/processed/saas/payments.csv', index=False
    )

    print(f"Invoices: {len(invoices)} records")
    print(f"Payments: {len(payments)} records")