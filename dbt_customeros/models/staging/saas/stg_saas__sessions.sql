with source as (
    select * from {{ source('saas_product', 'sessions') }}
),

renamed as (
    select
        session_id,
        customer_id,
        session_date::timestamp as session_date,
        duration_mins,
        device,
        created_at::timestamp as created_at
    from source
)

select * from renamed