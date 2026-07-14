with source as (
    select * from {{ source('fintech_accounts', 'accounts') }}
),

renamed as (
    select
        account_id,
        customer_id,
        account_type,
        balance,
        currency,
        status,
        opened_at::timestamp  as opened_at,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at
    from source
)

select * from renamed