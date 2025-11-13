{{ config(materialized='table', schema='FINAL') }}

WITH agg AS (
    SELECT
        trip_date,
        COUNT(*) AS total_trips,
        ROUND(AVG(trip_distance), 2) AS avg_distance,
        ROUND(SUM(total_amount), 2) AS total_revenue,
        ROUND(AVG(tip_pct), 2) AS avg_tip_pct,
        ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
    FROM {{ ref('stg__clean_trips') }}
    GROUP BY trip_date
)

SELECT *
FROM agg
ORDER BY trip_date;
