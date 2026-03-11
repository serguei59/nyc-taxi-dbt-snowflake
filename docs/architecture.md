# Architecture du projet NYC Taxi DWH

## Vue d'ensemble

Ce projet implémente un Data Warehouse complet sur Snowflake, alimenté par un pipeline
CI/CD GitHub Actions (Terraform → ETL Python → dbt).

## Flux de données

[NYC TLC Parquet files]
↓  Python ETL (merge_dynamic.py)
RAW.YELLOW_TAXI_TRIPS_V2          ← Snowflake, chargement mensuel
↓  dbt stg__clean_trips
STAGING.STG__CLEAN_TRIPS          ← Cast, filtrage, renommage colonnes
↓  dbt dim_* + fct__*
FINAL.DIM_DATE                    ← Dimension calendaire
FINAL.DIM_LOCATION                ← Dimension zones géographiques
FINAL.DIM_PAYMENT_TYPE            ← Dimension types de paiement
FINAL.DIM_RATE_CODE               ← Dimension codes tarifaires
FINAL.FCT__TRIPS                  ← Table de faits (grain : 1 trajet)
FINAL.FCT__DAILY_SUMMARY          ← Agrégat quotidien (data mart)
FINAL.FCT__ZONE_ANALYSIS          ← Agrégat par zone (data mart)
FINAL.FCT__HOURLY_PATTERNS        ← Agrégat horaire (data mart)
↓  Metabase (Docker local)
Dashboards BI                     ← Visualisation via rôle ANALYST

## Rôles Snowflake

| Rôle | Droits | Usage |
|---|---|---|
| `ACCOUNTADMIN` | Tous | Administration |
| `TRANSFORM` | SELECT RAW, CREATE/INSERT STAGING+FINAL | dbt + ETL |
| `ANALYST` | SELECT FINAL uniquement | Consommateurs BI (Metabase) |

## Pipeline CI/CD

Push sur dev/main
↓

1.Terraform apply → provisioning Snowflake (rôles, schémas, grants)
2.ETL Python → chargement Parquet → RAW (cache si déjà chargé)
3.dbt run → matérialisation STAGING + FINAL
4.dbt test → tests qualité (not_null, unique, accepted_values)
5.dbt source freshness → vérification fraîcheur RAW

## Stack technique

- **Terraform** `1.10.2` + provider Snowflake `2.10.1`
- **dbt-snowflake** `1.10.2`, **dbt-core** `1.10.13`
- **Python** `3.11` — pandas, snowflake-connector-python
- **GitHub Actions** — CI/CD automatisé
- **Terraform Cloud** — state backend (org: `nyc-taxi-project`, workspace: `rncp-e5`)
- **Metabase** — BI via Docker (connecteur Snowflake natif, rôle ANALYST)
