with source as (
    select * from {{ source('fintech_transactions', 'transactions') }}
),

renamed as (
    select
        transaction_id,
        step,
        transaction_type,
        amount,
        sender_id,
        sender_old_balance,
        sender_new_balance,
        receiver_id,
        receiver_old_balance,
        receiver_new_balance,
        (is_fraud = 1)         as is_fraud,
        (is_flagged_fraud = 1) as is_flagged_fraud
    from source
)

select * from renamed