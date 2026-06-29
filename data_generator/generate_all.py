"""
CustomerOS Master Data Generator
Runs all generators in the correct order
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from saas.crm_generator import (
    generate_customers as saas_customers,
    generate_accounts as saas_accounts,
    generate_contacts as saas_contacts,
)
from saas.product_usage_generator import (
    generate_sessions,
    generate_feature_usage,
)
from saas.support_generator import generate_tickets
from saas.billing_generator import (
    generate_invoices,
    generate_payments as saas_payments,
)
from saas.nps_generator import generate_nps_responses
from fintech.accounts_generator import (
    generate_customers as fintech_customers,
    generate_accounts as fintech_accounts,
)
from fintech.cards_generator import generate_cards
from fintech.loans_generator import (
    generate_loans,
    generate_repayments,
)

import pandas as pd

def run_all():
    start = time.time()
    print("\n" + "="*50)
    print("CustomerOS Data Generator")
    print("="*50)

    # ── SaaS Data ──────────────────────────────────────
    print("\n[SaaS] Generating customer data...")
    os.makedirs('data/processed/saas', exist_ok=True)

    customers = saas_customers(1000)
    accounts = saas_accounts(customers)
    contacts = saas_contacts(customers)
    customers.to_csv('data/processed/saas/customers.csv', index=False)
    accounts.to_csv('data/processed/saas/accounts.csv', index=False)
    contacts.to_csv('data/processed/saas/contacts.csv', index=False)
    print(f"{len(customers)} customers")
    print(f"{len(accounts)} accounts")
    print(f"{len(contacts)} contacts")

    print("\n[SaaS] Generating product usage...")
    sessions = generate_sessions(customers)
    feature_usage = generate_feature_usage(customers)
    sessions.to_csv('data/processed/saas/sessions.csv', index=False)
    feature_usage.to_csv('data/processed/saas/feature_usage.csv', index=False)
    print(f"{len(sessions)} sessions")
    print(f"{len(feature_usage)} feature usage records")

    print("\n[SaaS] Generating support tickets...")
    tickets = generate_tickets(customers)
    tickets.to_csv('data/processed/saas/tickets.csv', index=False)
    print(f"{len(tickets)} tickets")

    print("\n[SaaS] Generating billing data...")
    invoices = generate_invoices(customers)
    payments = saas_payments(invoices)
    invoices.to_csv('data/processed/saas/invoices.csv', index=False)
    payments.to_csv('data/processed/saas/payments.csv', index=False)
    print(f"{len(invoices)} invoices")
    print(f"{len(payments)} payments")

    print("\n[SaaS] Generating NPS responses...")
    nps = generate_nps_responses(customers)
    nps.to_csv('data/processed/saas/nps_responses.csv', index=False)
    print(f"{len(nps)} NPS responses")

    # ── Fintech Data ───────────────────────────────────
    print("\n[Fintech] Generating customer accounts...")
    os.makedirs('data/processed/fintech', exist_ok=True)

    fin_customers = fintech_customers(2000)
    fin_accounts = fintech_accounts(fin_customers)
    fin_customers.to_csv('data/processed/fintech/customers.csv', index=False)
    fin_accounts.to_csv('data/processed/fintech/accounts.csv', index=False)
    print(f"{len(fin_customers)} customers")
    print(f"{len(fin_accounts)} accounts")

    print("\n[Fintech] Generating cards...")
    cards = generate_cards(fin_accounts)
    cards.to_csv('data/processed/fintech/cards.csv', index=False)
    print(f"{len(cards)} cards")

    print("\n[Fintech] Generating loans...")
    loans = generate_loans(fin_customers)
    repayments = generate_repayments(loans)
    loans.to_csv('data/processed/fintech/loans.csv', index=False)
    repayments.to_csv('data/processed/fintech/repayments.csv', index=False)
    print(f"{len(loans)} loans")
    print(f"{len(repayments)} repayments")

    elapsed = round(time.time() - start, 1)
    print(f"\n{'='*50}")
    print(f"All data generated in {elapsed}s")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    run_all()