CREATE OR REPLACE TABLE fct_injury_cases AS
SELECT
    incident_id,
    event_date,
    EXTRACT(YEAR FROM event_date) AS event_year,
    EXTRACT(MONTH FROM event_date) AS event_month,
    EXTRACT(DAYOFWEEK FROM event_date) AS event_day_of_week,

    employer,
    city,
    state,
    zip_code,
    latitude,
    longitude,

    primary_naics,
    SUBSTR(primary_naics, 1, 2) AS naics_2_digit,
    SUBSTR(primary_naics, 1, 3) AS naics_3_digit,

    hospitalized_count,
    amputation_count,
    loss_of_eye_count,

    CASE
        WHEN amputation_count > 0 OR loss_of_eye_count > 0 THEN 1
        ELSE 0
    END AS high_severity_outcome,

    nature_title,
    body_part_title,
    event_title,
    source_title,
    secondary_source_title,

    final_narrative

FROM stg_severe_injuries;