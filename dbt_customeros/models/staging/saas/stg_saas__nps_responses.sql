with source as (
    select * from {{ source('saas_nps', 'responses') }}
),

renamed as (
    select
        response_id,
        customer_id,
        score,
        category,
        comment,
        submitted_at::timestamp as submitted_at,
        created_at::timestamp   as created_at
    from source
)

select * from renamed