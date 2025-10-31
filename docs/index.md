# NYC Taxi ETL & dbt Pipeline

Welcome to the NYC Taxi ETL & dbt Snowflake project!  

## Project Repository
Check out the GitHub repository: [NYC Taxi dbt Snowflake](https://github.com/serguei59/nyc-taxi-dbt-snowflake)

## Project Overview
This project automates the full ETL pipeline for NYC Taxi data and runs dbt transformations on Snowflake. It includes:

- Snowflake setup with `SnowSQL`
- Python ETL for data download and ingestion
- dbt transformations, tests, and documentation generation
- Scheduling and manual triggering via GitHub Actions

## 📖 Documentation

- [1. Snowflake Setup](./setup.md)
- [2. Data Ingestion (Python ETL)](./ingestion.md)
- [3. Data Transformations (dbt)](./transformation.md)
- [4. dbt Documentation](./dbt_docs/index.html) (generated automatically)

## Quick Start

### Prerequisites
- A Snowflake account with a dedicated `TRANSFORM` role user
- GitHub repository access and secrets setup (see below)
- Python 3.11 installed (handled in GitHub Actions)

### GitHub Secrets Required
Create the following repository secrets:

| Secret Name           | Description                                         |
|----------------------|-----------------------------------------------------|
| `SNOWFLAKE_ACCOUNT`   | Snowflake account name                              |
| `SNOWFLAKE_USER`      | Snowflake user for setup (ACCOUNTADMIN)            |
| `SNOWFLAKE_PASSWORD`  | Password for the setup user                         |
| `SNOWFLAKE_ROLE`      | Role used for setup (ACCOUNTADMIN)                 |
| `SNOWFLAKE_WAREHOUSE` | Warehouse for ETL and dbt                           |
| `SNOWFLAKE_DATABASE`  | Target database                                     |
| `SNOWFLAKE_SCHEMA`    | Target schema                                       |
| `DBT_PASSWORD`        | Password for dbt user (`TRANSFORM` role)           |

### Running the Workflow
- **Manual Trigger**: Go to the Actions tab → Select `Full ETL + dbt Pipeline` → Click `Run workflow`
- **Scheduled**: Configured via GitHub Actions `schedule` event (cron)

### Artifacts
- dbt documentation and reports are saved in `artifacts/dbt_docs/` for review.

### Navigation
- [1. Snowflake Setup](./setup.md)

