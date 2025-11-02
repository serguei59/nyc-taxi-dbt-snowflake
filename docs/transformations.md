# 🧱 Data Transformation Pipeline – NYC Taxi Data (dbt + Snowflake)

**Navigation:**  
[Home](./index.md) • [Setup](./setup.md) • [Ingestion](./ingestion.md) • [dbt_test](./data_quality.md)


## 🎯 Objective

This section of the project implements the **data transformation and modeling pipeline** in **Snowflake** using **dbt Core**, fully aligned with industrial best practices.

The pipeline follows a standard architecture:

```
RAW (ingested) → STAGING (cleaned & enriched) → FINAL (analytics)
```

---

## ⚙️ Technical Context

### 🔸 Technologies

* **Snowflake** – Cloud data warehouse for storage and compute
* **dbt Core** – SQL-based transformation and modeling framework
* **Python (`merge_dynamic.py`)** – Initial ingestion script writing to RAW schema
* **dbt tests & docs** – Automated data quality and documentation

### 🔸 Architecture Overview

| Layer       | Description                        | Example Tables                                                                       |
| ----------- | ---------------------------------- | ------------------------------------------------------------------------------------ |
| **RAW**     | Raw data loaded from Parquet files | `RAW.YELLOW_TAXI_TRIPS`                                                              |
| **STAGING** | Cleaned and enriched data          | `STAGING.STG__CLEAN_TRIPS`                                                           |
| **FINAL**   | Aggregated and analytical tables   | `FINAL.FCT__DAILY_SUMMARY`, `FINAL.FCT__ZONE_ANALYSIS`, `FINAL.FCT__HOURLY_PATTERNS` |

---

## 🧩 dbt Modeling

### 🗂️ 1. Data Source Declaration (`raw__sources.yml`)

Defines the raw Snowflake source for downstream models.

```yaml
version: 2

sources:
  - name: RAW
    schema: RAW
    description: "Raw Snowflake tables imported from Parquet files"
    tables:
      - name: YELLOW_TAXI_TRIPS
        description: "NYC Yellow Taxi 2024–2025 data ingested via Python pipeline"
```

---

### 🧹 2. STAGING Model (`stg__clean_trips.sql`)

Cleans, filters, and enriches the data according to project specifications.

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

### 📆 3. FINAL Model #1 (`fct__daily_summary.sql`)

Aggregated daily metrics.

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

### 🗺️ 4. FINAL Model #2 (`fct__zone_analysis.sql`)

Zone-based analysis.

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

### 🕒 5. FINAL Model #3 (`fct__hourly_patterns.sql`)

Hourly trends analysis.

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

### 🧪 6. Data Quality Tests (`schema.yml`)

```yaml
version: 2

models:
  - name: stg__clean_trips
    description: "Cleansed and enriched NYC Taxi trips dataset"
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
    description: "Daily KPIs and averages"
    columns:
      - name: TRIP_DATE
        tests: [not_null]

  - name: fct__zone_analysis
    description: "Pickup zone-level analysis"
    columns:
      - name: PICKUP_ZONE
        tests: [not_null]

  - name: fct__hourly_patterns
    description: "Hourly travel and revenue patterns"
    columns:
      - name: PICKUP_HOUR
        tests: [not_null]
```

---

## 🧠 Validation & Execution

```bash
dbt debug               # Validate Snowflake connection
dbt run                 # Run all transformations
dbt test                # Execute all data quality checks
dbt docs generate       # Build project documentation
dbt docs serve          # Launch interactive dbt docs & lineage view
```

---

## ✅ Compliance Summary

| Requirement                        | Model/File                 | Status |
| ---------------------------------- | -------------------------- | ------ |
| Data cleaning & normalization      | `stg__clean_trips.sql`     | ✅      |
| Time and tip enrichments           | `stg__clean_trips.sql`     | ✅      |
| Daily aggregation                  | `fct__daily_summary.sql`   | ✅      |
| Zone-based analysis                | `fct__zone_analysis.sql`   | ✅      |
| Hourly analysis                    | `fct__hourly_patterns.sql` | ✅      |
| Data tests & documentation         | `schema.yml` + dbt docs    | ✅      |
| RAW → STAGING → FINAL architecture | All models                 | ✅      |

---

## 🧩 Conclusion

This dbt transformation layer implements:

* A **modular and reproducible architecture**
* **Version-controlled SQL transformations**
* **Automated data validation and lineage documentation**
* **Full compliance with industrial-grade Snowflake standards**

The transformation pipeline is **robust, auditable, and production-ready**.

### Navigation
- [Home](./index.md)
- [dbt Documentation](./dbt_docs/index.html)