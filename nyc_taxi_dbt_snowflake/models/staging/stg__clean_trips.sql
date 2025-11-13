{{ config(
    materialized='table',
    schema='STAGING'
) }}

WITH source AS (
    SELECT * 
    FROM {{ source('RAW', 'YELLOW_TAXI_TRIPS_V2') }}
),

cleaned AS (
    SELECT
        CAST(VENDORID AS INTEGER) AS vendor_id,
        CAST(TPEP_PICKUP_DATETIME AS TIMESTAMP_NTZ) AS pickup_datetime,
        CAST(TPEP_DROPOFF_DATETIME AS TIMESTAMP_NTZ) AS dropoff_datetime,

        DATEDIFF('minute', TPEP_PICKUP_DATETIME, TPEP_DROPOFF_DATETIME) AS trip_duration_min,
        TRIP_DISTANCE AS trip_distance,
        TOTAL_AMOUNT AS total_amount,
        TIP_AMOUNT AS tip_amount,
        FARE_AMOUNT AS fare_amount,
        ROUND((TIP_AMOUNT / NULLIF(FARE_AMOUNT, 0)) * 100, 2) AS tip_pct,

        CAST(PULOCATIONID AS INTEGER) AS pu_location_id,
        CAST(DOLOCATIONID AS INTEGER) AS do_location_id,
        CAST(PASSENGER_COUNT AS INTEGER) AS passenger_count,
        CAST(PAYMENT_TYPE AS VARCHAR) AS payment_type,
        CAST(RATECODEID AS INTEGER) AS ratecode_id,

        MTA_TAX AS mta_tax,
        EXTRA AS extra,
        TOLLS_AMOUNT AS tolls_amount,
        IMPROVEMENT_SURCHARGE AS improvement_surcharge,
        CONGESTION_SURCHARGE AS congestion_surcharge,
        AIRPORT_FEE AS airport_fee,

        -- Temporal dimensions
        DATE(TPEP_PICKUP_DATETIME) AS trip_date,
        EXTRACT(HOUR FROM TPEP_PICKUP_DATETIME) AS pickup_hour,
        EXTRACT(MONTH FROM TPEP_PICKUP_DATETIME) AS pickup_month,

        CURRENT_TIMESTAMP() AS ingestion_ts

    FROM source
    WHERE TOTAL_AMOUNT >= 0
      AND TRIP_DISTANCE BETWEEN 0.1 AND 100
      AND TPEP_DROPOFF_DATETIME > TPEP_PICKUP_DATETIME
      AND PULOCATIONID IS NOT NULL
      AND DOLOCATIONID IS NOT NULL
      AND PASSENGER_COUNT BETWEEN 1 AND 6
)

SELECT * 
FROM cleaned;
