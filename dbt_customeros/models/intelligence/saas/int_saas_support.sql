with tickets as (
    select * from {{ ref('stg_saas__tickets') }}
),

agg as (
    select
        customer_id,
        count(*) filter (where created_at >= current_date - interval '90 days') as tickets_90d,
        count(*) filter (where severity = 'high' and created_at >= current_date - interval '90 days') as high_severity_90d,
        avg(resolution_hours) as avg_resolution_hours
    from tickets
    group by customer_id
),

scored as (
    select
        *,
        case
            when tickets_90d = 0 then 100
            when tickets_90d <= 2 then 80
            when tickets_90d <= 5 then 50
            when tickets_90d <= 10 then 20
            else 0
        end as volume_score,

        case
            when high_severity_90d = 0 then 100
            when high_severity_90d = 1 then 60
            when high_severity_90d = 2 then 30
            else 0
        end as severity_score,

        case
            when avg_resolution_hours is null then 100
            when avg_resolution_hours <= 4  then 100
            when avg_resolution_hours <= 24 then 75
            when avg_resolution_hours <= 72 then 40
            else 10
        end as resolution_score
    from agg
)

select
    customer_id,
    tickets_90d,
    high_severity_90d,
    avg_resolution_hours,
    volume_score,
    severity_score,
    resolution_score,
    round((volume_score * 0.4) + (severity_score * 0.4) + (resolution_score * 0.2), 1) as support_score
from scored