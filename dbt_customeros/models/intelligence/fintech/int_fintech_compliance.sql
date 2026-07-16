with customers as (
    select * from {{ ref('stg_fintech__customers') }}
)

select
    customer_id,
    kyc_status,
    is_active,
    case
        when kyc_status = 'verified' then 100
        when kyc_status = 'pending'  then 50
        when kyc_status = 'rejected' then 0
        else 40
    end as kyc_score,
    case when is_active then 100 else 0 end as active_status_score
from customers