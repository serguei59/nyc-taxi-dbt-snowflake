# 🧱 Transformation Pipeline – NYC Taxi Data (dbt + Snowflake)

## 🎯 Objectif de la section
Cette partie du projet a pour objectif de construire la **chaîne de transformation et de modélisation des données** dans Snowflake à l’aide de **dbt Core**, conformément aux exigences du brief Data Engineering Simplon.

L’approche suit la logique d’un pipeline industriel :
```
RAW (brut) → STAGING (nettoyé & enrichi) → FINAL (analytique)
```

---

## ⚙️ Contexte technique

### 🔸 Technologies
- **Snowflake** : Data Warehouse Cloud pour le stockage et les calculs.
- **dbt Core** : outil de transformation de données SQL as code.
- **Python (merge_dynamic.py)** : ingestion initiale vers le schéma RAW.
- **dbt tests + docs** : validation et documentation automatisées.

### 🔸 Architecture globale
| Niveau | Description | Exemple de table |
|--------|--------------|------------------|
| **RAW** | Données brutes importées depuis les fichiers Parquet | `RAW.YELLOW_TAXI_TRIPS` |
| **STAGING** | Données nettoyées et enrichies | `STAGING.STG__CLEAN_TRIPS` |
| **FINAL** | Tables agrégées prêtes à l’analyse | `FINAL.FCT__DAILY_SUMMARY`, `FINAL.FCT__ZONE_ANALYSIS`, `FINAL.FCT__HOURLY_PATTERNS` |

---

## 🧩 Modélisation dans dbt

### 🗂️ 1. Source de données : `raw__sources.yml`

Déclaration de la source brute utilisée pour les transformations.

```yaml
version: 2

sources:
  - name: RAW
    schema: RAW
    description: "Tables brutes importées dans Snowflake depuis les fichiers Parquet"
    tables:
      - name: YELLOW_TAXI_TRIPS
        description: "Données NYC Taxi 2024–2025 chargées via le script Python d’ingestion"
```

---

### 🧹 2. Modèle STAGING : `stg__clean_trips.sql`

Ce modèle nettoie, filtre et enrichit les données selon les exigences du brief.

```sql
{{ config(materialized='table', schema='STAGING') }}

WITH source AS (
    SELECT * FROM {{ source('RAW', 'YELLOW_TAXI_TRIPS') }}
),

cleaned AS (
    SELECT
        VENDORID,
        TPEP_PICKUP_DATETIME,
        TPEP_DROPOFF_DATETIME,
        DATEDIFF('minute', TPEP_PICKUP_DATETIME, TPEP_DROPOFF_DATETIME) AS TRIP_DURATION_MIN,
        TRIP_DISTANCE,
        TOTAL_AMOUNT,
        TIP_AMOUNT,
        FARE_AMOUNT,
        ROUND((TIP_AMOUNT / NULLIF(FARE_AMOUNT, 0)) * 100, 2) AS TIP_PCT,
        PULOCATIONID,
        DOLOCATIONID,
        PASSENGER_COUNT,
        PAYMENT_TYPE,
        RATECODEID,
        MTA_TAX,
        EXTRA,
        TOLLS_AMOUNT,
        IMPROVEMENT_SURCHARGE,
        CONGESTION_SURCHARGE,
        AIRPORT_FEE,
        -- Dimensions temporelles
        DATE(TPEP_PICKUP_DATETIME) AS TRIP_DATE,
        HOUR(TPEP_PICKUP_DATETIME) AS PICKUP_HOUR,
        MONTH(TPEP_PICKUP_DATETIME) AS PICKUP_MONTH
    FROM source
    WHERE TOTAL_AMOUNT >= 0
      AND TRIP_DISTANCE BETWEEN 0.1 AND 100
      AND TPEP_DROPOFF_DATETIME > TPEP_PICKUP_DATETIME
      AND PULOCATIONID IS NOT NULL
      AND DOLOCATIONID IS NOT NULL
)

SELECT * FROM cleaned
```

---

### 📆 3. Modèle FINAL #1 : `fct__daily_summary.sql`

```sql
{{ config(materialized='table', schema='FINAL') }}

SELECT
    TRIP_DATE,
    COUNT(*) AS TOTAL_TRIPS,
    ROUND(AVG(TRIP_DISTANCE), 2) AS AVG_DISTANCE,
    ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE,
    ROUND(AVG(TIP_PCT), 2) AS AVG_TIP_PCT,
    ROUND(AVG(TRIP_DURATION_MIN), 2) AS AVG_DURATION_MIN
FROM {{ ref('stg__clean_trips') }}
GROUP BY TRIP_DATE
ORDER BY TRIP_DATE
```

---

### 🗺️ 4. Modèle FINAL #2 : `fct__zone_analysis.sql`

```sql
{{ config(materialized='table', schema='FINAL') }}

SELECT
    PULOCATIONID AS PICKUP_ZONE,
    COUNT(*) AS TOTAL_TRIPS,
    ROUND(AVG(TOTAL_AMOUNT), 2) AS AVG_REVENUE,
    ROUND(AVG(TRIP_DISTANCE), 2) AS AVG_DISTANCE,
    ROUND(AVG(TRIP_DURATION_MIN), 2) AS AVG_DURATION,
    ROUND(AVG(TIP_PCT), 2) AS AVG_TIP_PCT
FROM {{ ref('stg__clean_trips') }}
GROUP BY PULOCATIONID
ORDER BY TOTAL_TRIPS DESC
```

---

### 🕒 5. Modèle FINAL #3 : `fct__hourly_patterns.sql`

```sql
{{ config(materialized='table', schema='FINAL') }}

SELECT
    PICKUP_HOUR,
    COUNT(*) AS TOTAL_TRIPS,
    ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE,
    ROUND(AVG(TRIP_DISTANCE), 2) AS AVG_DISTANCE,
    ROUND(AVG(TRIP_DURATION_MIN), 2) AS AVG_DURATION_MIN,
    ROUND(AVG(TIP_PCT), 2) AS AVG_TIP_PCT
FROM {{ ref('stg__clean_trips') }}
GROUP BY PICKUP_HOUR
ORDER BY PICKUP_HOUR
```

---

### 🧪 6. Tests de qualité (`schema.yml`)

```yaml
version: 2

models:
  - name: stg__clean_trips
    columns:
      - name: TRIP_DISTANCE
        tests:
          - not_null
          - accepted_range:
              min_value: 0
              max_value: 100
      - name: TOTAL_AMOUNT
        tests:
          - not_null
          - accepted_range:
              min_value: 0
      - name: PULOCATIONID
        tests: [not_null]
      - name: DOLOCATIONID
        tests: [not_null]

  - name: fct__daily_summary
    columns:
      - name: TRIP_DATE
        tests: [not_null]

  - name: fct__zone_analysis
    columns:
      - name: PICKUP_ZONE
        tests: [not_null]

  - name: fct__hourly_patterns
    columns:
      - name: PICKUP_HOUR
        tests: [not_null]
```

---

## 🧠 Validation et exécution

```bash
dbt debug
dbt run
dbt test
dbt docs generate
dbt docs serve
```

---

## ✅ Conformité au brief

| Exigence | Modèle/Fichier | Statut |
|-----------|----------------|--------|
| Nettoyage complet | `stg__clean_trips.sql` | ✅ |
| Enrichissement temporel & pourboire | `stg__clean_trips.sql` | ✅ |
| Table journalière | `fct__daily_summary.sql` | ✅ |
| Table par zone | `fct__zone_analysis.sql` | ✅ |
| Table horaire | `fct__hourly_patterns.sql` | ✅ |
| Tests qualité & doc | `schema.yml` + `dbt docs` | ✅ |
| Architecture 3-niveaux | RAW → STAGING → FINAL | ✅ |
