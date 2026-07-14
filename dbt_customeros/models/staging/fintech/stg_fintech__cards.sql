with source as (
    select * from {{ source('fintech_cards', 'cards') }}
),

renamed as (
    select
        card_id,
        account_id,
        customer_id,
        card_type,
        card_network,
        status,
        issued_at::timestamp    as issued_at,
        expires_at::timestamp   as expires_at,
        last_used_at::timestamp as last_used_at,
        created_at::timestamp   as created_at,
        updated_at::timestamp   as updated_at
    from source
)

select * from renamed