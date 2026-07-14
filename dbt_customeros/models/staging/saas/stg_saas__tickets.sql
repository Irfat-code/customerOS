with source as (
    select * from {{ source('saas_support', 'tickets') }}
),

renamed as (
    select
        ticket_id,
        customer_id,
        subject,
        severity,
        status,
        resolution_hours,
        created_at::timestamp  as created_at,
        resolved_at::timestamp as resolved_at,
        updated_at::timestamp  as updated_at
    from source
)

select * from renamed