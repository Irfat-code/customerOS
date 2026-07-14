with source as (
    select * from {{ source('saas_product', 'feature_usage') }}
),

renamed as (
    select
        usage_id,
        customer_id,
        feature_name,
        usage_count,
        usage_date::timestamp as usage_date,
        created_at::timestamp as created_at
    from source
)

select * from renamed