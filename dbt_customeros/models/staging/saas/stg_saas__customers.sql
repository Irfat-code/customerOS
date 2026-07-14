with source as (
    select * from {{ source('saas_crm', 'customers') }}
),

renamed as (
    select
        customer_id,
        company_name,
        email,
        industry,
        country,
        plan,
        segment,
        mrr,
        arr,
        is_churned,
        customer_since::timestamp        as customer_since,
        churned_at::timestamp            as churned_at,
        created_at::timestamp            as created_at,
        updated_at::timestamp            as updated_at
    from source
)

select * from renamed