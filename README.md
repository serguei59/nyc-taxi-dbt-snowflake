# NYC Taxi Data Warehouse

> A production-grade, fully automated data warehouse built on Snowflake —
> ingesting 50 million+ NYC Yellow Taxi trips across 23 months,
> modeled as a star schema, tested, historized, and ready for BI consumption.

---

## What this project demonstrates

Modern data engineering is not about moving files. It is about building systems
that are **reproducible**, **observable**, **governed**, and **resilient by design**.

This project implements the full data warehouse lifecycle on a real-world dataset:

- Raw ingestion of NYC TLC Parquet files via a Python ETL pipeline
- Infrastructure provisioned and version-controlled with Terraform
- Data transformation and quality enforcement with dbt
- Star schema modeling (fact table + 4 dimension tables) ready for Power BI
- SCD Type 2 historization via dbt snapshots
- Role-based access control with least-privilege enforcement
- Snowflake Time Travel for point-in-time recovery
- End-to-end CI/CD pipeline running on every commit

Zero manual steps. Zero credentials in code. Zero compromises on data quality.

---

## Data pipeline

```
NYC TLC Open Data  (monthly Parquet releases)
         |
         |  Python ETL — pandas + snowflake-connector-python
         |  Dynamic MERGE — idempotent, cache-aware, ~50M rows
         v
RAW.YELLOW_TAXI_TRIPS_V2
         |
         |  dbt — stg__clean_trips
         |  Type casting, null filtering, column aliasing
         v
STAGING.STG__CLEAN_TRIPS
         |
         +---------> FINAL.DIM_DATE            calendar attributes
         +---------> FINAL.DIM_LOCATION         NYC TLC zone registry
         +---------> FINAL.DIM_PAYMENT_TYPE     TLC payment codes
         +---------> FINAL.DIM_RATE_CODE        TLC rate codes
         +---------> FINAL.FCT__TRIPS           trip-grain fact table
         +---------> FINAL.FCT__DAILY_SUMMARY   pre-aggregated data mart
         +---------> FINAL.FCT__ZONE_ANALYSIS   zone-level analytics
         +---------> FINAL.FCT__HOURLY_PATTERNS time-of-day patterns
         |
         |  dbt snapshot — SCD Type 2
         v
SNAPSHOTS.SCD__CLEAN_TRIPS
```

Infrastructure is declared in Terraform and applied automatically on every push.

---

## Stack

| Concern | Technology |
|---|---|
| Data warehouse | Snowflake Standard |
| Transformation | dbt-core 1.10.13 · dbt-snowflake 1.10.2 |
| Infrastructure as Code | Terraform 1.10.2 · snowflake provider 2.10.1 |
| ETL | Python 3.11 · pandas · snowflake-connector-python |
| CI/CD | GitHub Actions |
| State management | Terraform Cloud (org: nyc-taxi-project) |
| BI layer | Power BI — connected to FINAL schema |

---

## Repository structure

```
.
├── .github/workflows/ci-cd.yaml         pipeline: Terraform → ETL → dbt
├── terraform/                            roles, warehouses, schemas, grants
├── etl/
│   ├── download_parquet.py              TLC monthly file fetcher
│   └── merge_dynamic.py                 idempotent MERGE into RAW
├── nyc_taxi_dbt_snowflake/
│   ├── models/
│   │   ├── raw/        source declarations + freshness thresholds
│   │   ├── staging/    cleaning and normalization layer
│   │   └── final/      star schema — dims and facts
│   ├── snapshots/      SCD Type 2 change history
│   ├── tests/          custom singular data quality tests
│   └── seeds/          reference data (taxi zones)
└── docs/
    ├── architecture.md
    ├── star_schema.md        MCD · MLD · MPD
    ├── data_dictionary.md
    ├── time_travel.md
    └── guide_evaluateur.md
```

---

## CI/CD pipeline

Every push to `dev` or `main` triggers three sequential jobs:

```
1. terraform apply
   Provisions or updates Snowflake objects: roles (TRANSFORM, ANALYST),
   schemas (RAW, STAGING, FINAL, SNAPSHOTS), grants, warehouse.

2. python etl
   Downloads any new monthly Parquet files from NYC TLC.
   Executes a MERGE statement into RAW. Skips months already loaded (cache check).

3. dbt
   dbt deps          resolve package dependencies
   dbt run           materialize 57 models
   dbt test          enforce not_null, unique, accepted_values, dbt_expectations
   dbt snapshot      apply SCD Type 2 on staging layer
   dbt source freshness   validate RAW freshness (warn > 35d, error > 60d)
```

---

## Star schema

```
                     DIM_DATE
                    (date_id)
                        |
DIM_LOCATION  ----------+---------- FCT__TRIPS ---------- DIM_PAYMENT_TYPE
(location_id)     pu / do fk         (measures)           (payment_type_id)
                        |
                   DIM_RATE_CODE
                   (ratecode_id)
```

`FCT__TRIPS` carries 20 measures at trip grain:
`trip_distance`, `trip_duration_min`, `fare_amount`, `tip_amount`, `tip_pct`,
`total_amount`, `mta_tax`, `extra`, `tolls_amount`, `congestion_surcharge`, and more.

Full schema documentation: [docs/star_schema.md](docs/star_schema.md)

---

## Access control

Roles are provisioned by Terraform. No manual grants.

| Role | Scope | Principal |
|---|---|---|
| `ACCOUNTADMIN` | Full administrative access | Terraform |
| `TRANSFORM` | SELECT on RAW · full access on STAGING, FINAL, SNAPSHOTS | dbt, ETL |
| `ANALYST` | SELECT on FINAL only | Power BI, data consumers |

The `ANALYST` role enforces read-only access to the serving layer.
It cannot read raw or staging data.

---

## Data quality

| Check | Mechanism | Threshold |
|---|---|---|
| Source freshness | dbt source freshness on INGESTION_TS | warn 35d · error 60d |
| Primary key integrity | dbt unique + not_null tests | 0 failures tolerated |
| Accepted values | dbt accepted_values on payment_type, ratecode | standard TLC codes |
| Statistical bounds | dbt_expectations on fare, distance, duration | p99 outlier detection |
| Project standards | dbt_project_evaluator | naming, docs, test coverage |

---

## Resilience and recovery

**Snowflake Time Travel** is configured with a 7-day retention window on the RAW layer.
This enables point-in-time queries, before/after load comparisons, and instant table restore
via `UNDROP` — with no external backup infrastructure required.

See [docs/time_travel.md](docs/time_travel.md) for operational runbooks.

**SCD Type 2** snapshots preserve the full history of the staging layer.
Each row carries `dbt_valid_from` and `dbt_valid_to` timestamps,
enabling historical analysis of any data state at any point in time.

---

## Local setup

```bash
# provision infrastructure
cd terraform && terraform init && terraform apply

# load data
cd etl && pip install -r requirements.txt && python merge_dynamic.py

# run transformations
cd nyc_taxi_dbt_snowflake
dbt deps && dbt run && dbt test && dbt snapshot && dbt source freshness
```

---

## Documentation

- [Architecture overview](docs/architecture.md)
- [Star schema — MCD / MLD / MPD](docs/star_schema.md)
- [Data dictionary](docs/data_dictionary.md)
- [Time Travel runbook](docs/time_travel.md)
- [Evaluator guide](docs/guide_evaluateur.md)

---

## Dataset

Source: [NYC Taxi & Limousine Commission — TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
Coverage: January 2024 – November 2025 · 23 monthly Parquet files · ~50M trips
