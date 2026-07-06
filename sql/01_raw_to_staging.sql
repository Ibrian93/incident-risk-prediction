CREATE OR REPLACE TABLE stg_severe_injuries AS
WITH parsed AS (
    SELECT
        CAST(ID AS VARCHAR) AS incident_id,
        CAST(STRPTIME(EventDate, '%m/%d/%Y') AS DATE) AS event_date,

        Employer AS employer,
        City AS city,
        State AS state,
        Zip AS zip_code,
        Latitude AS latitude,
        Longitude AS longitude,
        CAST("Primary NAICS" AS VARCHAR) AS primary_naics,

        COALESCE(Hospitalized, 0) AS hospitalized_count,
        COALESCE(Amputation, 0) AS amputation_count,
        COALESCE("Loss of Eye", 0) AS loss_of_eye_count,

        "Final Narrative" AS final_narrative,

        Nature AS nature_code,
        NatureTitle AS nature_title,

        "Part of Body" AS body_part_code,
        "Part of Body Title" AS body_part_title,

        Event AS event_code,
        EventTitle AS event_title,

        Source AS source_code,
        SourceTitle AS source_title,

        "Secondary Source" AS secondary_source_code,
        "Secondary Source Title" AS secondary_source_title,

        FederalState AS federal_state_flag

    FROM raw_severe_injuries
)
SELECT *
FROM parsed
WHERE event_date IS NOT NULL;