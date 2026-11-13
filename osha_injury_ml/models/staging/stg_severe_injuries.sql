-- Remove exact source duplicates only. Conflicting report keys fail a data test.
with source_rows as (
    select distinct *
    from {{ source('osha', 'raw_severe_injuries') }}
)

select
    nullif(trim("ID"), '') as incident_id,
    nullif(trim("UPA"), '') as upa,
    cast(try_strptime(trim("EventDate"), '%m/%d/%Y') as date) as event_date,
    nullif(trim("Employer"), '') as employer,
    nullif(trim("Address1"), '') as main_address,
    nullif(trim("Address2"), '') as secondary_address,
    nullif(trim("City"), '') as city,
    nullif(upper(trim("State")), '') as state,
    nullif(trim("Zip"), '') as zip_code,
    try_cast(nullif(trim("Latitude"), '') as double) as latitude,
    try_cast(nullif(trim("Longitude"), '') as double) as longitude,
    nullif(trim("Primary NAICS"), '') as primary_naics,
    try_cast(nullif(trim("Hospitalized"), '') as integer) as hospitalized_count,
    try_cast(nullif(trim("Amputation"), '') as integer) as amputation_count,
    try_cast(nullif(trim("Loss of Eye"), '') as integer) as loss_of_eye_count,
    nullif(trim("Inspection"), '') as inspection,
    nullif(trim("Final Narrative"), '') as final_narrative,
    nullif(trim("Nature"), '') as nature_code,
    nullif(trim("NatureTitle"), '') as nature_title,
    nullif(trim("Part of Body"), '') as body_part_code,
    nullif(trim("Part of Body Title"), '') as body_part_title,
    nullif(trim("Event"), '') as event_code,
    nullif(trim("EventTitle"), '') as event_title,
    nullif(trim("Source"), '') as source_code,
    nullif(trim("SourceTitle"), '') as source_title,
    nullif(trim("Secondary Source"), '') as secondary_source_code,
    nullif(trim("Secondary Source Title"), '') as secondary_source_title,
    nullif(trim("FederalState"), '') as federal_state_flag
from source_rows
