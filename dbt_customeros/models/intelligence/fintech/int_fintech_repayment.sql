with loans as (
    select * from {{ ref('stg_fintech__loans') }}
),

repayments as (
    select * from {{ ref('stg_fintech__repayments') }}
),

repayment_agg as (
    select
        customer_id,
        count(*) as total_repayments,
        count(*) filter (where status = 'late')   as late_repayments,
        count(*) filter (where status = 'missed') as missed_repayments,
        sum(amount_due)  as total_due,
        sum(amount_paid) as total_paid
    from repayments
    group by customer_id
),

loan_agg as (
    select
        customer_id,
        count(*) as total_loans,
        count(*) filter (where status = 'defaulted') as defaulted_loans
    from loans
    group by customer_id
),

combined as (
    select
        coalesce(r.customer_id, l.customer_id) as customer_id,
        coalesce(r.total_repayments, 0)   as total_repayments,
        coalesce(r.late_repayments, 0)    as late_repayments,
        coalesce(r.missed_repayments, 0)  as missed_repayments,
        r.total_due,
        r.total_paid,
        coalesce(l.total_loans, 0)        as total_loans,
        coalesce(l.defaulted_loans, 0)    as defaulted_loans
    from repayment_agg r
    full outer join loan_agg l on r.customer_id = l.customer_id
),

scored as (
    select
        *,
        case
            when total_repayments = 0 then 100
            else greatest(0, 100 - (late_repayments * 15) - (missed_repayments * 40))
        end as repayment_score,

        case
            when total_loans = 0 then 100
            when defaulted_loans = 0 then 100
            else greatest(0, 100 - (defaulted_loans * 50))
        end as default_score
    from combined
)

select
    customer_id,
    total_loans,
    total_repayments,
    late_repayments,
    missed_repayments,
    defaulted_loans,
    repayment_score,
    default_score,
    round((repayment_score * 0.6) + (default_score * 0.4), 1) as repayment_health_score
from scored