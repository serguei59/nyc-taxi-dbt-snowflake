{{ config(materialized='table', schema='FINAL') }}

SELECT
    -- Clés étrangères vers les dimensions
    t.trip_date                     AS date_fk,
    t.pu_location_id                AS pu_location_fk,
    t.do_location_id                AS do_location_fk,
    CAST(t.payment_type AS INTEGER) AS payment_type_fk,
    t.ratecode_id                   AS ratecode_fk,

    -- Dimensions dégénérées (conservées dans la fact)
    t.vendor_id,
    t.pickup_datetime,
    t.dropoff_datetime,
    t.passenger_count,

    -- Mesures
    t.trip_distance,
    t.trip_duration_min,
    t.fare_amount,
    t.tip_amount,
    t.tip_pct,
    t.total_amount,
    t.mta_tax,
    t.extra,
    t.tolls_amount,
    t.improvement_surcharge,
    t.congestion_surcharge,
    t.airport_fee

FROM {{ ref('stg__clean_trips') }} t
