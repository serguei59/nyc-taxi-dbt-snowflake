{{ config(materialized='table', schema='FINAL') }}

WITH dates AS (
    SELECT DISTINCT trip_date
    FROM {{ ref('stg__clean_trips') }}
)

SELECT
    trip_date                                        AS date_id,
    EXTRACT(YEAR FROM trip_date)::INTEGER            AS year,
    EXTRACT(MONTH FROM trip_date)::INTEGER           AS month,
    EXTRACT(DAY FROM trip_date)::INTEGER             AS day,
    DAYOFWEEK(trip_date)                             AS day_of_week,
    DAYNAME(trip_date)                               AS day_name,
    MONTHNAME(trip_date)                             AS month_name,
    WEEKOFYEAR(trip_date)                            AS week_of_year,
    QUARTER(trip_date)                               AS quarter,
    IFF(DAYOFWEEK(trip_date) IN (0, 6), TRUE, FALSE) AS is_weekend
FROM dates
ORDER BY date_id
