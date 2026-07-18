{{ config(materialized='table') }}

with counts as (
    select 'saas_crm.customers' as table_name, count(*) as row_count from {{ source('saas_crm', 'customers') }}
    union all
    select 'saas_crm.accounts', count(*) from {{ source('saas_crm', 'accounts') }}
    union all
    select 'saas_crm.contacts', count(*) from {{ source('saas_crm', 'contacts') }}
    union all
    select 'saas_product.sessions', count(*) from {{ source('saas_product', 'sessions') }}
    union all
    select 'saas_product.feature_usage', count(*) from {{ source('saas_product', 'feature_usage') }}
    union all
    select 'saas_billing.invoices', count(*) from {{ source('saas_billing', 'invoices') }}
    union all
    select 'saas_billing.payments', count(*) from {{ source('saas_billing', 'payments') }}
    union all
    select 'saas_support.tickets', count(*) from {{ source('saas_support', 'tickets') }}
    union all
    select 'saas_nps.responses', count(*) from {{ source('saas_nps', 'responses') }}
    union all
    select 'fintech_accounts.customers', count(*) from {{ source('fintech_accounts', 'customers') }}
    union all
    select 'fintech_accounts.accounts', count(*) from {{ source('fintech_accounts', 'accounts') }}
    union all
    select 'fintech_cards.cards', count(*) from {{ source('fintech_cards', 'cards') }}
    union all
    select 'fintech_loans.loans', count(*) from {{ source('fintech_loans', 'loans') }}
    union all
    select 'fintech_loans.repayments', count(*) from {{ source('fintech_loans', 'repayments') }}
    union all
    select 'fintech_transactions.transactions', count(*) from {{ source('fintech_transactions', 'transactions') }}
)

select
    table_name,
    row_count,
    current_timestamp as checked_at
from counts