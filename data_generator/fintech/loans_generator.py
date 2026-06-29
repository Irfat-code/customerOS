"""
Fintech Loans Generator
Generates loan records with repayment patterns
including defaults and delays
"""
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker()
Faker.seed(42)
random.seed(42)

LOAN_PURPOSES = [
    'business_expansion', 'working_capital',
    'equipment_purchase', 'personal', 'education',
    'home_improvement', 'emergency', 'vehicle'
]


def generate_loans(
    customers_df: pd.DataFrame
) -> pd.DataFrame:
    """Generate loan records per customer."""
    loans = []
    loan_id = 1

    eligible = customers_df[
        customers_df['kyc_status'] == 'verified'
    ]

    for _, customer in eligible.iterrows():
        if random.random() < 0.3:  # 30% take a loan

            # Convert ISO string to datetime
            customer_created_at = datetime.fromisoformat(
                customer['created_at']
            )

            disbursed_at = fake.date_time_between(
                start_date=customer_created_at,
                end_date='now'
            )

            amount = round(random.uniform(500, 50000), 2)
            term_months = random.choice([3, 6, 12, 24, 36])
            due_date = disbursed_at + timedelta(
                days=30 * term_months
            )

            status = random.choices(
                ['active', 'completed', 'defaulted', 'overdue'],
                weights=[0.4, 0.4, 0.1, 0.1]
            )[0]

            loans.append({
                'loan_id':          f'LON-{str(loan_id).zfill(7)}',
                'customer_id':      customer['customer_id'],
                'amount':           amount,
                'currency':         'USD',
                'interest_rate':    round(random.uniform(8, 24), 2),
                'term_months':      term_months,
                'purpose':          random.choice(LOAN_PURPOSES),
                'status':           status,
                'disbursed_at':     disbursed_at.isoformat(),
                'due_date':         due_date.date().isoformat(),
                'created_at':       disbursed_at.isoformat(),
                'updated_at':       datetime.now().isoformat(),
            })

            loan_id += 1

    return pd.DataFrame(loans)


def generate_repayments(
    loans_df: pd.DataFrame
) -> pd.DataFrame:
    """Generate monthly repayment records."""
    repayments = []
    repayment_id = 1

    for _, loan in loans_df.iterrows():
        disbursed = datetime.fromisoformat(
            loan['disbursed_at']
        )

        monthly_payment = round(
            loan['amount'] / loan['term_months'], 2
        )

        months_elapsed = min(
            loan['term_months'],
            max(1, (datetime.now() - disbursed).days // 30)
        )

        for month in range(months_elapsed):
            due = disbursed + timedelta(
                days=30 * (month + 1)
            )

            if (
                loan['status'] == 'defaulted'
                and month > months_elapsed - 3
            ):
                status = random.choices(
                    ['missed', 'partial', 'paid'],
                    weights=[0.5, 0.3, 0.2]
                )[0]

            elif loan['status'] == 'overdue':
                status = random.choices(
                    ['paid', 'late', 'missed'],
                    weights=[0.5, 0.3, 0.2]
                )[0]

            else:
                status = random.choices(
                    ['paid', 'late'],
                    weights=[0.9, 0.1]
                )[0]

            paid_at = None
            amount_paid = 0

            if status == 'paid':
                paid_at = (
                    due + timedelta(
                        days=random.randint(0, 3)
                    )
                ).isoformat()
                amount_paid = monthly_payment

            elif status == 'late':
                paid_at = (
                    due + timedelta(
                        days=random.randint(4, 30)
                    )
                ).isoformat()
                amount_paid = monthly_payment

            elif status == 'partial':
                paid_at = due.isoformat()
                amount_paid = round(
                    monthly_payment *
                    random.uniform(0.3, 0.8),
                    2
                )

            repayments.append({
                'repayment_id': f'REP-{str(repayment_id).zfill(8)}',
                'loan_id':      loan['loan_id'],
                'customer_id':  loan['customer_id'],
                'amount_due':   monthly_payment,
                'amount_paid':  amount_paid,
                'status':       status,
                'due_date':     due.date().isoformat(),
                'paid_at':      paid_at,
                'created_at':   due.isoformat(),
            })

            repayment_id += 1

    return pd.DataFrame(repayments)


if __name__ == '__main__':
    customers = pd.read_csv(
        'data/processed/fintech/customers.csv'
    )

    print("Generating loans data...")

    loans = generate_loans(customers)
    repayments = generate_repayments(loans)

    os.makedirs(
        'data/processed/fintech',
        exist_ok=True
    )

    loans.to_csv(
        'data/processed/fintech/loans.csv',
        index=False
    )

    repayments.to_csv(
        'data/processed/fintech/repayments.csv',
        index=False
    )

    print(f"Loans: {len(loans)} records")
    print(f"Repayments: {len(repayments)} records")