{{ config(materialized='table', schema='FINAL') }}

WITH aggregated AS (
    SELECT
        pickup_hour,
        trip_date,
        total_amount,
        trip_distance,
        trip_duration_min,
        tip_pct
    FROM {{ ref('stg__clean_trips') }}
)

SELECT
    pickup_hour,
    trip_date,
    COUNT(*) AS total_trips,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
    ROUND(AVG(tip_pct), 2) AS avg_tip_pct
FROM aggregated
GROUP BY pickup_hour, trip_date
ORDER BY pickup_hour, trip_date
