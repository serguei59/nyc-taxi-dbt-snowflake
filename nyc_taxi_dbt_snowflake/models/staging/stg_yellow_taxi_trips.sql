{{ config(
    materialized='table',
    schema='STAGING',
    alias='clean_trips',
    tags=['staging', 'cleaning']
) }}

WITH raw_data AS (
    SELECT
        vendorid,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        pulocationid,
        dolocationid,
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        airport_fee
    FROM {{ source('raw', 'yellow_taxi_trips') }}
),

cleaned AS (
    SELECT
        *,
        -- ✅ Durée du trajet en minutes (arrondie)
        ROUND(DATEDIFF('minute', tpep_pickup_datetime, tpep_dropoff_datetime), 0) AS trip_duration_min,

        -- ✅ Vitesse moyenne (miles par heure, arrondie à 2 décimales)
        CASE 
            WHEN DATEDIFF('minute', tpep_pickup_datetime, tpep_dropoff_datetime) > 0 
            THEN ROUND((trip_distance / NULLIF(DATEDIFF('minute', tpep_pickup_datetime, tpep_dropoff_datetime), 0)) * 60, 2)
            ELSE NULL
        END AS avg_speed_mph,

        -- ✅ Pourcentage du pourboire (arrondi à 2 décimales)
        CASE 
            WHEN total_amount > 0 THEN ROUND((tip_amount / total_amount) * 100, 2)
            ELSE NULL
        END AS tip_percent,

        -- ✅ Dimensions temporelles
        DATE_TRUNC('hour', tpep_pickup_datetime) AS pickup_hour,
        DATE_TRUNC('day', tpep_pickup_datetime) AS pickup_day,
        DATE_TRUNC('month', tpep_pickup_datetime) AS pickup_month
    FROM raw_data
)

filtered AS (
    SELECT *
    FROM cleaned
    WHERE 
        -- ✅ Cohérence temporelle
        tpep_dropoff_datetime > tpep_pickup_datetime

        -- ✅ Distances réalistes
        AND trip_distance BETWEEN 0.1 AND 100

        -- ✅ Montants positifs
        AND fare_amount >= 0
        AND total_amount >= 0

        -- ✅ Zones connues
        AND pulocationid IS NOT NULL
        AND dolocationid IS NOT NULL

        -- ✅ Passenger count valide
        AND passenger_count BETWEEN 1 AND 6
)

SELECT *
FROM filtered;
