
---

**`docs/data_dictionary.md`**
```markdown
# Dictionnaire de données — NYC Taxi DWH

## RAW.YELLOW_TAXI_TRIPS_V2

Source : NYC TLC (Taxi & Limousine Commission) — fichiers Parquet mensuels.

| Colonne | Type | Description |
|---|---|---|
| VENDORID | INTEGER | Identifiant du fournisseur (1=Creative Mobile, 2=VeriFone) |
| TPEP_PICKUP_DATETIME | TIMESTAMP | Horodatage début de course |
| TPEP_DROPOFF_DATETIME | TIMESTAMP | Horodatage fin de course |
| PASSENGER_COUNT | INTEGER | Nombre de passagers |
| TRIP_DISTANCE | FLOAT | Distance en miles |
| RATECODEID | INTEGER | Code tarifaire appliqué |
| PULOCATIONID | INTEGER | Zone TLC de prise en charge |
| DOLOCATIONID | INTEGER | Zone TLC de dépose |
| PAYMENT_TYPE | INTEGER | Mode de paiement |
| FARE_AMOUNT | FLOAT | Montant tarifaire de base |
| EXTRA | FLOAT | Suppléments (rush hour, nuit) |
| MTA_TAX | FLOAT | Taxe MTA |
| TIP_AMOUNT | FLOAT | Pourboire |
| TOLLS_AMOUNT | FLOAT | Péages |
| IMPROVEMENT_SURCHARGE | FLOAT | Surcharge amélioration |
| TOTAL_AMOUNT | FLOAT | Montant total |
| CONGESTION_SURCHARGE | FLOAT | Surcharge congestion |
| AIRPORT_FEE | FLOAT | Frais aéroport |
| INGESTION_TS | TIMESTAMP | Horodatage chargement ETL |

## STAGING.STG__CLEAN_TRIPS

Données nettoyées et typées depuis RAW. Filtres appliqués :
- `TOTAL_AMOUNT >= 0`
- `TRIP_DISTANCE BETWEEN 0.1 AND 100`
- `DROPOFF > PICKUP`
- `PASSENGER_COUNT BETWEEN 1 AND 6`

| Colonne | Type | Description |
|---|---|---|
| vendor_id | INTEGER | Fournisseur |
| pickup_datetime | TIMESTAMP_NTZ | Début de course |
| dropoff_datetime | TIMESTAMP_NTZ | Fin de course |
| trip_duration_min | INTEGER | Durée en minutes |
| trip_distance | FLOAT | Distance en miles |
| total_amount | FLOAT | Montant total |
| tip_amount | FLOAT | Pourboire |
| fare_amount | FLOAT | Tarif de base |
| tip_pct | FLOAT | Pourboire en % du tarif |
| pu_location_id | INTEGER | Zone pickup |
| do_location_id | INTEGER | Zone dropoff |
| passenger_count | INTEGER | Passagers |
| payment_type | VARCHAR | Mode de paiement |
| ratecode_id | INTEGER | Code tarifaire |
| trip_date | DATE | Date de la course |
| pickup_hour | INTEGER | Heure de départ (0-23) |
| pickup_month | INTEGER | Mois de départ (1-12) |
| ingestion_ts | TIMESTAMP | Horodatage chargement |

## FINAL.DIM_DATE

| Colonne | Type | Description |
|---|---|---|
| date_id (PK) | DATE | Date (clé primaire) |
| year | INTEGER | Année |
| month | INTEGER | Mois (1-12) |
| day | INTEGER | Jour (1-31) |
| day_of_week | INTEGER | Jour semaine (0=Dim, 6=Sam) |
| day_name | VARCHAR | Nom du jour (Mon, Tue…) |
| month_name | VARCHAR | Nom du mois (Jan, Feb…) |
| week_of_year | INTEGER | Semaine de l'année |
| quarter | INTEGER | Trimestre (1-4) |
| is_weekend | BOOLEAN | TRUE si samedi ou dimanche |

## FINAL.DIM_LOCATION

| Colonne | Type | Description |
|---|---|---|
| location_id (PK) | INTEGER | Identifiant zone TLC |
| zone_name | VARCHAR | Nom de zone |
| borough | VARCHAR | Arrondissement NYC |

## FINAL.DIM_PAYMENT_TYPE

| Colonne | Type | Description |
|---|---|---|
| payment_type_id (PK) | INTEGER | Code paiement TLC |
| payment_type_label | VARCHAR | Libellé (Credit card, Cash…) |

## FINAL.DIM_RATE_CODE

| Colonne | Type | Description |
|---|---|---|
| ratecode_id (PK) | INTEGER | Code tarifaire TLC |
| rate_description | VARCHAR | Description (Standard, JFK…) |

## FINAL.FCT__TRIPS

Table de faits au grain trajet individuel.

| Colonne | Type | Description |
|---|---|---|
| date_fk | DATE | FK → DIM_DATE.date_id |
| pu_location_fk | INTEGER | FK → DIM_LOCATION.location_id |
| do_location_fk | INTEGER | FK → DIM_LOCATION.location_id |
| payment_type_fk | INTEGER | FK → DIM_PAYMENT_TYPE.payment_type_id |
| ratecode_fk | INTEGER | FK → DIM_RATE_CODE.ratecode_id |
| vendor_id | INTEGER | Fournisseur (dim dégénérée) |
| pickup_datetime | TIMESTAMP | Début de course |
| dropoff_datetime | TIMESTAMP | Fin de course |
| passenger_count | INTEGER | Passagers |
| trip_distance | FLOAT | Distance en miles |
| trip_duration_min | INTEGER | Durée en minutes |
| fare_amount | FLOAT | Tarif de base |
| tip_amount | FLOAT | Pourboire |
| tip_pct | FLOAT | % pourboire |
| total_amount | FLOAT | Montant total |
| mta_tax | FLOAT | Taxe MTA |
| extra | FLOAT | Suppléments |
| tolls_amount | FLOAT | Péages |
| improvement_surcharge | FLOAT | Surcharge amélioration |
| congestion_surcharge | FLOAT | Surcharge congestion |
| airport_fee | FLOAT | Frais aéroport |
