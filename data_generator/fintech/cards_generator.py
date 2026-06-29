"""
Fintech Cards Generator
Generates card records linked to customer accounts
"""
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker()
Faker.seed(42)
random.seed(42)

CARD_TYPES = ['debit', 'credit', 'prepaid', 'virtual']
CARD_NETWORKS = ['Visa', 'Mastercard', 'Verve']


def generate_cards(
    accounts_df: pd.DataFrame
) -> pd.DataFrame:
    """Generate cards per account."""
    cards = []
    card_id = 1

    for _, account in accounts_df.iterrows():
        if account['status'] != 'active':
            continue

        if random.random() < 0.7:  # 70% of active accounts have cards

            # Convert the ISO string to a datetime object
            opened_at = datetime.fromisoformat(account['opened_at'])

            issued_at = fake.date_time_between(
                start_date=opened_at,
                end_date='now'
            )

            expiry = issued_at + timedelta(days=365 * 3)

            last_used = (
                fake.date_time_between(
                    start_date=issued_at,
                    end_date='now'
                )
                if random.random() > 0.1
                else None
            )

            cards.append({
                'card_id':          f'CRD-{str(card_id).zfill(8)}',
                'account_id':       account['account_id'],
                'customer_id':      account['customer_id'],
                'card_type':        random.choice(CARD_TYPES),
                'card_network':     random.choice(CARD_NETWORKS),
                'status':           random.choices(
                    ['active', 'blocked', 'expired', 'cancelled'],
                    weights=[0.75, 0.1, 0.1, 0.05]
                )[0],
                'issued_at':        issued_at.isoformat(),
                'expires_at':       expiry.isoformat(),
                'last_used_at':     last_used.isoformat() if last_used else None,
                'created_at':       issued_at.isoformat(),
                'updated_at':       datetime.now().isoformat(),
            })

            card_id += 1

    return pd.DataFrame(cards)


if __name__ == '__main__':
    accounts = pd.read_csv('data/processed/fintech/accounts.csv')
    print("Generating cards data...")

    cards = generate_cards(accounts)

    os.makedirs('data/processed/fintech', exist_ok=True)
    cards.to_csv(
        'data/processed/fintech/cards.csv',
        index=False
    )

    print(f"Cards: {len(cards)} records")