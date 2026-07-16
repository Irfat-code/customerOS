with customers as (
    select * from {{ ref('stg_fintech__customers') }}
),

activity as (
    select * from {{ ref('int_fintech_activity') }}
),

repayment as (
    select * from {{ ref('int_fintech_repayment') }}
),

compliance as (
    select * from {{ ref('int_fintech_compliance') }}
),

joined as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.segment,
        c.country,
        c.kyc_status,
        c.is_active,

        coalesce(a.activity_score, 30) as activity_score,
        a.days_since_card_use,

        coalesce(r.repayment_health_score, 70) as repayment_health_score,
        (r.customer_id is not null)             as has_loan_history,
        coalesce(r.late_repayments, 0)          as late_repayments,
        coalesce(r.missed_repayments, 0)        as missed_repayments,
        coalesce(r.defaulted_loans, 0)          as defaulted_loans,

        -- KYC kept as a visible attribute for compliance reporting,
        -- but NOT included in the risk score. Validation showed every
        -- loan-holding customer is already KYC-verified (avg_kyc = 100.0
        -- across the board), so it has zero discriminating power within
        -- the population this score is meant to differentiate.
        coalesce(cp.kyc_score, 40) as kyc_score

    from customers c
    left join activity a    on c.customer_id = a.customer_id
    left join repayment r   on c.customer_id = r.customer_id
    left join compliance cp on c.customer_id = cp.customer_id
),

scored as (
    select
        *,
        round(
            (repayment_health_score * 0.80) +
            (activity_score         * 0.20)
        , 1) as risk_health_score
    from joined
)

select
    *,
    (missed_repayments > 0 or defaulted_loans > 0) as has_repayment_problem,
    case
        when risk_health_score >= 55 then 'Healthy'
        when risk_health_score >= 45 then 'At Risk'
        else 'Critical'
    end as risk_tier
from scored