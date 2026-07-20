CREATE OR REPLACE TABLE ml_injury_features AS
SELECT
    incident_id,
    event_date,
    event_year,
    event_month,
    event_day_of_week,

    COALESCE(state, 'Unknown') AS state,
    COALESCE(naics_2_digit, 'Unknown') AS naics_2_digit,
    COALESCE(naics_3_digit, 'Unknown') AS naics_3_digit,

    COALESCE(nature_title, 'Unknown') AS nature_title,
    COALESCE(body_part_title, 'Unknown') AS body_part_title,
    COALESCE(event_title, 'Unknown') AS event_title,
    COALESCE(source_title, 'Unknown') AS source_title,
    COALESCE(secondary_source_title, 'Unknown') AS secondary_source_title,

    COALESCE(final_narrative, '') AS final_narrative,

    high_severity_outcome

FROM fct_injury_cases
WHERE event_year IS NOT NULL
  AND high_severity_outcome IS NOT NULL;