select
    incident_id,
    event_date,
    event_year,
    event_month,
    event_day_of_week,

    state,
    primary_naics,
    naics_2_digit,
    naics_3_digit,

    nature_title,
    body_part_title,
    event_title,
    source_title,
    secondary_source_title,

    high_severity_outcome

from {{ ref('int_injury_cases') }}
