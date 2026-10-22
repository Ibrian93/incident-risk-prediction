select
    incident_id,
    event_date,
    extract(year from event_date) as event_year,
    extract(month from event_date) as event_month,
    extract(dayofweek from event_date) as event_day_of_week,

    employer,
    city,
    state,
    zip_code,
    latitude,
    longitude,

    primary_naics,
    substr(primary_naics, 1, 2) as naics_2_digit,
    substr(primary_naics, 1, 3) as naics_3_digit,

    hospitalized_count,
    amputation_count,
    loss_of_eye_count,

    case
        when amputation_count > 0 or loss_of_eye_count > 0 then 1
        else 0
    end as high_severity_outcome,

    nature_title,
    body_part_title,
    event_title,
    source_title,
    secondary_source_title,

    final_narrative

from {{ ref('stg_severe_injuries') }}
