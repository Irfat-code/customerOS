with accounts as (
    select * from {{ ref('stg_fintech__accounts') }}
),

cards as (
    select * from {{ ref('stg_fintech__cards') }}
),

card_agg as (
    select
        customer_id,
        max(last_used_at) as last_card_used_at,
        count(*) filter (where status = 'active') as active_cards
    from cards
    group by customer_id
),

account_agg as (
    select
        customer_id,
        count(*) filter (where status = 'active') as active_accounts,
        count(*) as total_accounts,
        sum(balance) as total_balance
    from accounts
    group by customer_id
),

combined as (
    select
        a.customer_id,
        a.active_accounts,
        a.total_accounts,
        a.total_balance,
        coalesce(c.active_cards, 0) as active_cards,
        c.last_card_used_at,
        (current_date - c.last_card_used_at::date) as days_since_card_use
    from account_agg a
    left join card_agg c on a.customer_id = c.customer_id
),

scored as (
    select
        *,
        case
            when total_accounts = 0 then 0
            else round(100.0 * active_accounts / total_accounts)
        end as account_status_score,

        case
            when days_since_card_use is null then 20
            when days_since_card_use <= 14 then 100
            when days_since_card_use <= 30 then 75
            when days_since_card_use <= 60 then 40
            when days_since_card_use <= 90 then 15
            else 0
        end as card_activity_score
    from combined
)

select
    customer_id,
    active_accounts,
    total_accounts,
    total_balance,
    active_cards,
    days_since_card_use,
    account_status_score,
    card_activity_score,
    round((account_status_score * 0.5) + (card_activity_score * 0.5), 1) as activity_score
from scored