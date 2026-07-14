with responses as (
    select * from {{ ref('stg_saas__nps_responses') }}
),

latest as (
    select distinct on (customer_id)
        customer_id,
        score,
        category,
        submitted_at
    from responses
    order by customer_id, submitted_at desc
)

select
    customer_id,
    score as latest_nps_score,
    category as latest_nps_category,
    submitted_at as latest_nps_date,
   case
        when category = 'Promoter'  then 100
        when category = 'Passive'   then 60
        when category = 'Detractor' then 20
        else 50
    end as sentiment_score
from latest