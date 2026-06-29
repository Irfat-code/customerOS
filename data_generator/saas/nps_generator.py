"""
SaaS NPS Survey Generator
Generates Net Promoter Score responses
with realistic sentiment patterns
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

PROMOTER_COMMENTS = [
    "Love the product! Changed how we work.",
    "Incredible support team. Very responsive.",
    "Best tool we've used. Highly recommend.",
    "Game changer for our analytics workflow.",
    "Saves us hours every week. Worth every penny.",
]

PASSIVE_COMMENTS = [
    "Good product but missing some features.",
    "Works well most of the time.",
    "Support could be faster.",
    "Decent value for money.",
    "Getting better with each update.",
]

DETRACTOR_COMMENTS = [
    "Too many bugs lately.",
    "Support takes too long to respond.",
    "Too expensive for what it offers.",
    "Had major outages last month.",
    "Considering switching to a competitor.",
    "Data sync issues are frustrating.",
]


def generate_nps_responses(
    customers_df: pd.DataFrame,
    days: int = 90
) -> pd.DataFrame:
    """Generate NPS survey responses."""
    responses = []
    response_id = 1
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for _, customer in customers_df.iterrows():
        # Each customer gets 1-3 survey responses
        n_responses = random.randint(1, 3)

        for i in range(n_responses):
            submitted_at = fake.date_time_between(
                start_date=start_date,
                end_date=end_date
            )

            # Score distribution based on customer health
            if customer['is_churned']:
                score = random.choices(
                    range(11),
                    weights=[8,7,6,5,4,3,2,2,2,1,1]
                )[0]
            elif customer['segment'] == 'Enterprise':
                score = random.choices(
                    range(11),
                    weights=[1,1,1,1,2,3,4,5,8,10,10]
                )[0]
            else:
                score = random.choices(
                    range(11),
                    weights=[2,2,2,2,3,4,5,6,8,8,8]
                )[0]

            # NPS category
            if score >= 9:
                category = 'Promoter'
                comment = random.choice(PROMOTER_COMMENTS)
            elif score >= 7:
                category = 'Passive'
                comment = random.choice(PASSIVE_COMMENTS)
            else:
                category = 'Detractor'
                comment = random.choice(DETRACTOR_COMMENTS)

            responses.append({
                'response_id':  f'NPS-{str(response_id).zfill(7)}',
                'customer_id':  customer['customer_id'],
                'score':        score,
                'category':     category,
                'comment':      comment,
                'submitted_at': submitted_at.isoformat(),
                'created_at':   submitted_at.isoformat(),
            })
            response_id += 1

    return pd.DataFrame(responses)


if __name__ == '__main__':
    customers = pd.read_csv('data/processed/saas/customers.csv')
    print("Generating NPS data...")

    responses = generate_nps_responses(customers)

    os.makedirs('data/processed/saas', exist_ok=True)
    responses.to_csv(
        'data/processed/saas/nps_responses.csv', index=False
    )
    print(f"NPS responses: {len(responses)} records")