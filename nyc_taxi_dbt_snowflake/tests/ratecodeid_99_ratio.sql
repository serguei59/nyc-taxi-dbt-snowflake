{{ config(severity: "warn") }}
SELECT
    CASE
        WHEN (COUNT_IF(RATECODEID = 99) * 1.0 / COUNT(*)) <= 0.02 THEN 0
        ELSE 1
    END AS failed
FROM {{ ref('stg__clean_trips') }}