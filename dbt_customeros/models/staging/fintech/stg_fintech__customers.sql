with source as (
    select * from {{ source('fintech_accounts', 'customers') }}
),

renamed as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        phone,
        country,
        segment,
        kyc_status,
        is_active,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at
    from source
)

select * from renamed