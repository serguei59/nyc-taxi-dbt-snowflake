{{ config(materialized='table', schema='FINAL') }}

WITH base AS (
    SELECT
        pu_location_id,
        total_amount,
        trip_distance,
        trip_duration_min,
        tip_pct
    FROM {{ ref('stg__clean_trips') }}
),

zone_agg AS (
    SELECT
        pu_location_id AS pickup_zone,
        COUNT(*) AS total_trips,
        ROUND(AVG(total_amount), 2) AS avg_revenue,
        ROUND(AVG(trip_distance), 2) AS avg_distance,
        ROUND(AVG(trip_duration_min), 2) AS avg_duration,
        ROUND(AVG(tip_pct), 2) AS avg_tip_pct
    FROM base
    GROUP BY pu_location_id
)

SELECT *
FROM zone_agg
ORDER BY total_trips DESC

