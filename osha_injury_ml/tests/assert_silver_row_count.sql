-- Cleaning must retain every distinct source record.
select 1 as row_count_mismatch
where
    (select count(*) from {{ ref('stg_severe_injuries') }})
    !=
    (select count(*) from (
        select distinct * from {{ source('osha', 'raw_severe_injuries') }}
    ) as distinct_source)
