{% snapshot schema_snapshot %}

{{
    config(
        target_schema='observability',
        unique_key="schema_name || '.' || table_name || '.' || column_name",
        strategy='check',
        check_cols=['data_type', 'is_nullable']
    )
}}

select
    table_schema as schema_name,
    table_name,
    column_name,
    data_type,
    is_nullable
from information_schema.columns
where table_schema in (
    'saas_crm', 'saas_product', 'saas_billing', 'saas_support', 'saas_nps',
    'fintech_accounts', 'fintech_cards', 'fintech_loans', 'fintech_transactions'
)

{% endsnapshot %}