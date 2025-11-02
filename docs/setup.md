
# ✅ Snowflake Setup – NYC Yellow Taxi Project

**Navigation:**  
[Home](./index.md) • [Ingestion](./ingestion.md) • [Transformations](./transformations.md) • [dbt_test](./data_quality.md)

This document provides the complete setup guide to initialize Snowflake infrastructure and configure a local or CI data engineering environment used by the NYC Taxi dbt project.

---

## Table of contents

- [Workstation setup](#workstation-setup)
- [Snowflake infrastructure](#snowflake-infrastructure)
  - [Database & schemas](#database--schemas)
  - [Warehouse](#warehouse)
  - [Role & user management](#role--user-management)
  - [Permissions](#permissions)
  - [dbt profile example](#dbt-profile-example)
- [Status & verification](#status--verification)
- [Useful links](#useful-links)

---

## Workstation setup

Ensure your local or CI runner includes:

- **SnowSQL (Snowflake CLI)** — install with the official installer:
\`\`\`bash
sudo apt-get update && sudo apt-get install -y libssl-dev libffi-dev
curl -O https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.2/linux_x86_64/snowsql-1.2.26-linux_x86_64.bash
chmod +x snowsql-1.2.26-linux_x86_64.bash
./snowsql-1.2.26-linux_x86_64.bash -y
\`\`\`

- **dbt (Snowflake adapter)**:
\`\`\`bash
pip install dbt-snowflake
\`\`\`

- **Python** and \`python-dotenv\` for loading \`.env\` locally; use GitHub Secrets in CI.

- **Git** and GitHub Actions for the pipeline.

---

## Snowflake infrastructure

### Database & schemas
\`\`\`sql
create database if not exists NYC_TAXI_DB;

create schema if not exists NYC_TAXI_DB.RAW;
create schema if not exists NYC_TAXI_DB.STAGING;
create schema if not exists NYC_TAXI_DB.FINAL;
\`\`\`

### Warehouse
\`\`\`sql
create warehouse if not exists NYC_TAXI_WH
  warehouse_size = 'MEDIUM'
  auto_suspend = 60
  auto_resume = true;
\`\`\`

### Role & user management
\`\`\`sql
create role if not exists TRANSFORM;

create user if not exists DBT
  password = 'custom_password!'
  default_role = TRANSFORM
  default_warehouse = NYC_TAXI_WH
  must_change_password = false;

grant role TRANSFORM to user DBT;
\`\`\`

### Permissions
\`\`\`sql
grant usage, operate on warehouse NYC_TAXI_WH to role TRANSFORM;
grant usage on database NYC_TAXI_DB to role TRANSFORM;

grant usage on schema NYC_TAXI_DB.RAW to role TRANSFORM;
grant usage on schema NYC_TAXI_DB.STAGING to role TRANSFORM;
grant usage on schema NYC_TAXI_DB.FINAL to role TRANSFORM;

grant select on all tables in schema NYC_TAXI_DB.RAW to role TRANSFORM;
grant select on future tables in schema NYC_TAXI_DB.RAW to role TRANSFORM;

grant create table, create view on schema NYC_TAXI_DB.STAGING to role TRANSFORM;
grant create table, create view on schema NYC_TAXI_DB.FINAL to role TRANSFORM;
\`\`\`

### dbt profile example (\`~/.dbt/profiles.yml\`)
\`\`\`yaml
nyc_taxi_dbt_snowflake:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "<your_account>"
      user: DBT
      password: "<your_password>"
      role: TRANSFORM
      warehouse: NYC_TAXI_WH
      database: NYC_TAXI_DB
      schema: STAGING
      threads: 1
      client_session_keep_alive: False
\`\`\`

---

## Status & verification

Manual verification examples:

\`\`\`bash
snowsql -a <ACCOUNT> -u <ADMIN_USER> -p '<PASSWORD>' -r ACCOUNTADMIN -w NYC_TAXI_WH -d NYC_TAXI_DB -s RAW
snowsql -a <ACCOUNT> -u DBT -p '<DBT_PASSWORD>' -r TRANSFORM -w NYC_TAXI_WH -d NYC_TAXI_DB -s STAGING
\`\`\`

---

## Useful links

- Repository: https://github.com/serguei59/nyc-taxi-dbt-snowflake
- Workflows: https://github.com/serguei59/nyc-taxi-dbt-snowflake/actions
- dbt docs: https://docs.getdbt.com/
- Snowflake docs: https://docs.snowflake.com/en/sql-reference

---
### Navigation
- [Home](./index.md)
- [2. Data Ingestion (Python ETL)](./ingestion.md)
EOF
