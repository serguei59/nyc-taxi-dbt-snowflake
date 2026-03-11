{{ config(
    materialized='table',
    schema='STAGING'
) }}

WITH source AS (
    SELECT *
    FROM {{ source('RAW', 'YELLOW_TAXI_TRIPS_V2') }}
),

-- RAW timestamps were stored as microseconds interpreted as seconds by Snowflake COPY INTO.
-- Fix: extract epoch seconds (the inflated µs value) and divide by 1,000,000 to recover real seconds.
fixed AS (
    SELECT
        *,
        TO_TIMESTAMP_NTZ(DATE_PART('epoch_second', TPEP_PICKUP_DATETIME)  / 1000000) AS pickup_ts,
        TO_TIMESTAMP_NTZ(DATE_PART('epoch_second', TPEP_DROPOFF_DATETIME) / 1000000) AS dropoff_ts
    FROM source
),

cleaned AS (
    SELECT
        CAST(VENDORID AS INTEGER)                              AS vendor_id,
        pickup_ts                                              AS pickup_datetime,
        dropoff_ts                                             AS dropoff_datetime,

        DATEDIFF('minute', pickup_ts, dropoff_ts)             AS trip_duration_min,
        TRIP_DISTANCE                                         AS trip_distance,
        TOTAL_AMOUNT                                          AS total_amount,
        TIP_AMOUNT                                            AS tip_amount,
        FARE_AMOUNT                                           AS fare_amount,
        ROUND((TIP_AMOUNT / NULLIF(FARE_AMOUNT, 0)) * 100, 2) AS tip_pct,

        CAST(PULOCATIONID AS INTEGER)                         AS pu_location_id,
        CAST(DOLOCATIONID AS INTEGER)                         AS do_location_id,
        CAST(PASSENGER_COUNT AS INTEGER)                      AS passenger_count,
        CAST(PAYMENT_TYPE AS VARCHAR)                         AS payment_type,
        CAST(RATECODEID AS INTEGER)                           AS ratecode_id,

        MTA_TAX                                               AS mta_tax,
        EXTRA                                                 AS extra,
        TOLLS_AMOUNT                                          AS tolls_amount,
        IMPROVEMENT_SURCHARGE                                 AS improvement_surcharge,
        CONGESTION_SURCHARGE                                  AS congestion_surcharge,
        AIRPORT_FEE                                           AS airport_fee,

        -- Temporal dimensions
        DATE(pickup_ts)                                       AS trip_date,
        EXTRACT(HOUR FROM pickup_ts)                          AS pickup_hour,
        EXTRACT(MONTH FROM pickup_ts)                         AS pickup_month,

        CURRENT_TIMESTAMP()                                   AS ingestion_ts

    FROM fixed
    WHERE TOTAL_AMOUNT >= 0
      AND TRIP_DISTANCE BETWEEN 0.1 AND 100
      AND dropoff_ts > pickup_ts
      AND DATEDIFF('minute', pickup_ts, dropoff_ts) BETWEEN 1 AND 1440
      AND DATE(pickup_ts) BETWEEN '2024-01-01' AND '2025-11-30'
      AND PULOCATIONID IS NOT NULL
      AND DOLOCATIONID IS NOT NULL
      AND PASSENGER_COUNT BETWEEN 1 AND 6
)

SELECT *
FROM cleaned
