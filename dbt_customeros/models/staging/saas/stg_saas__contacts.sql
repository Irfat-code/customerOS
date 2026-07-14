with source as (
    select * from {{ source('saas_crm', 'contacts') }}
),

renamed as (
    select
        contact_id,
        customer_id,
        first_name,
        last_name,
        email,
        role,
        is_primary,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at
    from source
)

select * from renamed