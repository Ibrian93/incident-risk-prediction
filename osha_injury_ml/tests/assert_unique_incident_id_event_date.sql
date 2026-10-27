select
    incident_id,
    event_date,
    count(*) as row_count

from {{ ref('stg_severe_injuries') }}

group by
    incident_id,
    event_date

having count(*) > 1