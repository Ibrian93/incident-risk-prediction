-- A malformed non-empty source value must not become a silent silver null.
select "ID", "EventDate"
from {{ source('osha', 'raw_severe_injuries') }}
where
    try_strptime(trim("EventDate"), '%m/%d/%Y') is null
    or (nullif(trim("Latitude"), '') is not null
        and try_cast(trim("Latitude") as double) is null)
    or (nullif(trim("Longitude"), '') is not null
        and try_cast(trim("Longitude") as double) is null)
    or (nullif(trim("Hospitalized"), '') is not null
        and try_cast(trim("Hospitalized") as integer) is null)
    or (nullif(trim("Amputation"), '') is not null
        and try_cast(trim("Amputation") as integer) is null)
    or (nullif(trim("Loss of Eye"), '') is not null
        and try_cast(trim("Loss of Eye") as integer) is null)
