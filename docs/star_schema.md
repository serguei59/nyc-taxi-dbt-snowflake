# Modélisation en étoile — NYC Taxi DWH

## MCD — Modèle Conceptuel de Données

[DATE] ----< [TRAJET] >---- [ZONE PICKUP]
|
+---------- [ZONE DROPOFF]
|
+---------- [TYPE PAIEMENT]
|
+---------- [CODE TARIFAIRE]


Un TRAJET est associé à :
- 1 DATE (date du trajet)
- 1 ZONE DE PRISE EN CHARGE
- 1 ZONE DE DÉPOSE
- 1 TYPE DE PAIEMENT
- 1 CODE TARIFAIRE

## MLD — Modèle Logique de Données


DIM_DATE (date_id PK, year, month, day, day_name, month_name,
week_of_year, quarter, is_weekend)

DIM_LOCATION (location_id PK, zone_name, borough)

DIM_PAYMENT_TYPE (payment_type_id PK, payment_type_label)

DIM_RATE_CODE (ratecode_id PK, rate_description)

FCT__TRIPS (date_fk FK→DIM_DATE,
pu_location_fk FK→DIM_LOCATION,
do_location_fk FK→DIM_LOCATION,
payment_type_fk FK→DIM_PAYMENT_TYPE,
ratecode_fk FK→DIM_RATE_CODE,
vendor_id, pickup_datetime, dropoff_datetime,
passenger_count, trip_distance, trip_duration_min,
fare_amount, tip_amount, tip_pct, total_amount,
mta_tax, extra, tolls_amount, improvement_surcharge,
congestion_surcharge, airport_fee)


## MPD — Modèle Physique de Données (Snowflake)

Toutes les tables sont dans le schéma `FINAL` de la base `NYC_TAXI_DB_RNCP`.

| Table | Matérialisation | Lignes approx. |
|---|---|---|
| `DIM_DATE` | TABLE | ~700 (2024-01 à 2025-11) |
| `DIM_LOCATION` | TABLE | ~263 zones |
| `DIM_PAYMENT_TYPE` | TABLE | 5 |
| `DIM_RATE_CODE` | TABLE | 7 |
| `FCT__TRIPS` | TABLE | ~50M trajets |

## Diagramme en étoile

          DIM_DATE
         (date_id)
             │
             │ date_fk
             │
DIM_LOCATION ────┤ pu_location_fk    FCT__TRIPS    payment_type_fk ──── DIM_PAYMENT_TYPE
(location_id)    ├─────────────────(mesures)──────────────────────────  (payment_type_id)
│ do_location_fk
│
│ ratecode_fk
│
DIM_RATE_CODE
(ratecode_id)

