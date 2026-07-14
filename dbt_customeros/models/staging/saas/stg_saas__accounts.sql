with source as (
    select * from {{ source('saas_crm', 'accounts') }}
),

renamed as (
    select
        account_id,
        customer_id,
        plan,
        contract_value,
        billing_cycle,
        auto_renew,
        start_date::timestamp    as start_date,
        renewal_date::timestamp  as renewal_date,
        created_at::timestamp    as created_at,
        updated_at::timestamp    as updated_at
    from source
)

select * from renamed