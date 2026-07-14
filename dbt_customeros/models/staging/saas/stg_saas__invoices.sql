with source as (
    select * from {{ source('saas_billing', 'invoices') }}
),

renamed as (
    select
        invoice_id,
        customer_id,
        amount,
        currency,
        status,
        invoice_date::timestamp as invoice_date,
        due_date::timestamp     as due_date,
        created_at::timestamp   as created_at,
        updated_at::timestamp   as updated_at
    from source
)

select * from renamed