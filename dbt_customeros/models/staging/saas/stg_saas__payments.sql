with source as (
    select * from {{ source('saas_billing', 'payments') }}
),

renamed as (
    select
        payment_id,
        invoice_id,
        customer_id,
        amount_paid,
        currency,
        method,
        status,
        paid_at::timestamp    as paid_at,
        created_at::timestamp as created_at
    from source
)

select * from renamed