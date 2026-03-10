{{ config(materialized='table', schema='FINAL') }}

WITH all_zones AS (
    SELECT DISTINCT pu_location_id AS location_id
    FROM {{ ref('stg__clean_trips') }}
    UNION
    SELECT DISTINCT do_location_id AS location_id
    FROM {{ ref('stg__clean_trips') }}
)

SELECT
    location_id,
    'Zone ' || location_id::VARCHAR AS zone_name,
    CASE
        WHEN location_id BETWEEN 1   AND 69  THEN 'Manhattan'
        WHEN location_id BETWEEN 70  AND 133 THEN 'Brooklyn'
        WHEN location_id BETWEEN 134 AND 199 THEN 'Queens'
        WHEN location_id BETWEEN 200 AND 235 THEN 'Bronx'
        WHEN location_id BETWEEN 236 AND 263 THEN 'Staten Island'
        ELSE 'Unknown'
    END AS borough
FROM all_zones
ORDER BY location_id
