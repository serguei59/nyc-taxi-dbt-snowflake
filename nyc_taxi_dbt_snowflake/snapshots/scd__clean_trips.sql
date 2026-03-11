{% snapshot scd__clean_trips %}

{{
    config(
        target_schema='SNAPSHOTS',
        unique_key='trip_key',
        strategy='check',
        check_cols=[
            'total_amount',
            'fare_amount',
            'tip_amount',
            'trip_distance',
            'passenger_count'
        ]
    )
}}

SELECT
    {{ dbt_utils.generate_surrogate_key([
        'pickup_datetime',
        'dropoff_datetime',
        'pu_location_id',
        'do_location_id',
        'vendor_id'
    ]) }} AS trip_key,

    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    pu_location_id,
    do_location_id,
    passenger_count,
    trip_distance,
    trip_duration_min,
    fare_amount,
    tip_amount,
    tip_pct,
    total_amount,
    mta_tax,
    extra,
    tolls_amount,
    improvement_surcharge,
    congestion_surcharge,
    airport_fee,
    payment_type,
    ratecode_id,
    trip_date,
    pickup_hour,
    pickup_month

FROM {{ ref('stg__clean_trips') }}

{% endsnapshot %}
