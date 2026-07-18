-- Fails if any monitored column exceeds a 5% null rate.
select *
from {{ ref('obs_null_rates') }}
where null_rate_pct > 5