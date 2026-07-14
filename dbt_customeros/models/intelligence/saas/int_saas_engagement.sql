with sessions as (
    select * from {{ ref('stg_saas__sessions') }}
),

feature_usage as (
    select * from {{ ref('stg_saas__feature_usage') }}
),

session_agg as (
    select
        customer_id,
        max(session_date) as last_session_date,
        count(*) filter (where session_date >= current_date - interval '30 days') as sessions_30d,
        count(*) filter (where session_date >= current_date - interval '90 days') as sessions_90d
    from sessions
    group by customer_id
),

feature_agg as (
    select
        customer_id,
        count(distinct feature_name) as distinct_features_used
    from feature_usage
    group by customer_id
),

combined as (
    select
        s.customer_id,
        s.last_session_date,
        (current_date - s.last_session_date::date) as days_since_last_session,
        s.sessions_30d,
        s.sessions_90d,
        coalesce(f.distinct_features_used, 0) as distinct_features_used
    from session_agg s
    left join feature_agg f on s.customer_id = f.customer_id
),

scored as (
    select
        *,
        case
            when days_since_last_session <= 7  then 100
            when days_since_last_session <= 14 then 80
            when days_since_last_session <= 30 then 60
            when days_since_last_session <= 60 then 30
            when days_since_last_session <= 90 then 10
            else 0
        end as recency_score,

        case
            when sessions_30d >= 20 then 100
            when sessions_30d >= 10 then 75
            when sessions_30d >= 5  then 50
            when sessions_30d >= 1  then 25
            else 0
        end as frequency_score,

        least(distinct_features_used * 10, 100) as breadth_score
    from combined
)

select
    customer_id,
    last_session_date,
    days_since_last_session,
    sessions_30d,
    sessions_90d,
    distinct_features_used,
    recency_score,
    frequency_score,
    breadth_score,
    round((recency_score * 0.5) + (frequency_score * 0.3) + (breadth_score * 0.2), 1) as engagement_score
from scored