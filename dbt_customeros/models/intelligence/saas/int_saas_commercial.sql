with accounts as (
    select * from {{ ref('stg_saas__accounts') }}
),

payments as (
    select * from {{ ref('stg_saas__payments') }}
),

payment_issues as (
    select
        customer_id,
        count(*) filter (where status in ('failed', 'late')) as failed_or_late_payments,
        count(*) as total_payments
    from payments
    group by customer_id
),

combined as (
    select
        a.customer_id,
        a.account_id,
        a.contract_value,
        a.auto_renew,
        a.renewal_date,
        (a.renewal_date::date - current_date) as days_to_renewal,
        coalesce(p.failed_or_late_payments, 0) as failed_or_late_payments,
        coalesce(p.total_payments, 0) as total_payments
    from accounts a
    left join payment_issues p on a.customer_id = p.customer_id
),

scored as (
    select
        *,
        case when auto_renew then 100 else 40 end as auto_renew_score,

        case
            when auto_renew then 100
            when days_to_renewal <= 30 then 20
            when days_to_renewal <= 60 then 50
            when days_to_renewal <= 90 then 75
            else 100
        end as renewal_score,

        case
            when total_payments = 0 then 100
            else greatest(0, 100 - (failed_or_late_payments * 25))
        end as payment_score
    from combined
)

select
    customer_id,
    account_id,
    contract_value,
    auto_renew,
    renewal_date,
    days_to_renewal,
    failed_or_late_payments,
    auto_renew_score,
    renewal_score,
    payment_score,
    round((auto_renew_score * 0.4) + (renewal_score * 0.3) + (payment_score * 0.3), 1) as commercial_score
from scored