with source as (
    select * from {{ source('fintech_loans', 'loans') }}
),

renamed as (
    select
        loan_id,
        customer_id,
        amount,
        currency,
        interest_rate,
        term_months,
        purpose,
        status,
        disbursed_at::timestamp as disbursed_at,
        due_date::timestamp     as due_date,
        created_at::timestamp   as created_at,
        updated_at::timestamp   as updated_at
    from source
)

select * from renamed