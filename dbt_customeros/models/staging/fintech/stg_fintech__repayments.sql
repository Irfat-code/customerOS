with source as (
    select * from {{ source('fintech_loans', 'repayments') }}
),

renamed as (
    select
        repayment_id,
        loan_id,
        customer_id,
        amount_due,
        amount_paid,
        status,
        due_date::timestamp   as due_date,
        paid_at::timestamp    as paid_at,
        created_at::timestamp as created_at
    from source
)

select * from renamed