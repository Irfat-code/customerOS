{{ config(materialized='table') }}

with checks as (
    select
        'saas_crm.customers' as table_name,
        'customer_id' as column_name,
        count(*) as total_rows,
        count(*) filter (where customer_id is null) as null_count
    from {{ source('saas_crm', 'customers') }}
    union all
    select
        'saas_crm.customers', 'email',
        count(*), count(*) filter (where email is null)
    from {{ source('saas_crm', 'customers') }}
    union all
    select
        'fintech_accounts.customers', 'customer_id',
        count(*), count(*) filter (where customer_id is null)
    from {{ source('fintech_accounts', 'customers') }}
    union all
    select
        'fintech_accounts.customers', 'email',
        count(*), count(*) filter (where email is null)
    from {{ source('fintech_accounts', 'customers') }}
    union all
    select
        'saas_billing.invoices', 'customer_id',
        count(*), count(*) filter (where customer_id is null)
    from {{ source('saas_billing', 'invoices') }}
    union all
    select
        'fintech_loans.loans', 'customer_id',
        count(*), count(*) filter (where customer_id is null)
    from {{ source('fintech_loans', 'loans') }}
)

select
    table_name,
    column_name,
    total_rows,
    null_count,
    round(100.0 * null_count / nullif(total_rows, 0), 2) as null_rate_pct,
    current_timestamp as checked_at
from checks