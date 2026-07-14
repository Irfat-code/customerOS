with customers as (
    select * from {{ ref('stg_saas__customers') }}
),

engagement as (
    select * from {{ ref('int_saas_engagement') }}
),

commercial as (
    select * from {{ ref('int_saas_commercial') }}
),

support as (
    select * from {{ ref('int_saas_support') }}
),

sentiment as (
    select * from {{ ref('int_saas_sentiment') }}
),

joined as (
    select
        c.customer_id,
        c.company_name,
        c.segment,
        c.plan,
        c.mrr,
        c.arr,
        c.is_churned,
        c.churned_at,

        coalesce(e.engagement_score, 50) as engagement_score,
        (e.customer_id is not null)      as has_engagement_data,

        coalesce(cm.commercial_score, 50) as commercial_score,
        cm.days_to_renewal,
        cm.auto_renew,
        (cm.customer_id is not null)      as has_commercial_data,

        coalesce(s.support_score, 100) as support_score,
        (s.customer_id is not null)    as has_support_data,

        coalesce(sm.sentiment_score, 50) as sentiment_score,
        sm.latest_nps_category,
        (sm.customer_id is not null)     as has_sentiment_data

    from customers c
    left join engagement e on c.customer_id = e.customer_id
    left join commercial cm on c.customer_id = cm.customer_id
    left join support s     on c.customer_id = s.customer_id
    left join sentiment sm  on c.customer_id = sm.customer_id
),

scored as (
    select
        *,
        round(
        (engagement_score * 0.20) +
        (commercial_score * 0.10) +
        (support_score    * 0.35) +
        (sentiment_score  * 0.35)
    , 1) as health_score
    from joined
)

select
    *,
    case
        when health_score >= 55 then 'Healthy'
        when health_score >= 50 then 'At Risk'
        else 'Critical'
    end as health_tier
from scored