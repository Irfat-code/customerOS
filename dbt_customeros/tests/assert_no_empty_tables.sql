-- Fails if any monitored table has zero rows.
-- dbt singular tests "pass" when this query returns NO rows.
select *
from {{ ref('obs_row_counts') }}
where row_count = 0