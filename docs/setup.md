# ✅ Snowflake Setup – NYC Yellow Taxi Project

This document summarizes the full setup of the Snowflake infrastructure, as well as the installation and configuration of the local data engineering workstation.

---

## 💻 Workstation Setup (Local Dev Environment)

To ensure reproducibility and industrial-grade setup, a dedicated workstation was configured with:

### 🧰 Tools Installed

- **SnowSQL** (Snowflake CLI)
  - Installed via `.rpm` then converted with `alien` to `.deb`
  ```bash
  sudo alien -d snowflake-snowsql-1.4.5-1.x86_64.rpm
  sudo dpkg -i snowflake-snowsql_1.4.5-2_amd64.deb
  ```

- **dbt Core** (open-source version for Snowflake)
  - Installed via pip:
  ```bash
  pip install dbt-snowflake
  ```

- **Python & Environment Management**
  - Python `.env` file for secret management.
  - `python-dotenv` to securely read secrets into scripts.
  - Git + GitHub Pages for versioning and documentation.

- **GitHub Setup**
  - Branching strategy: `main`, `setup`, then `dev`
  - Used `.gitignore` to exclude local data and secrets

---

## 🏗️ Snowflake Infrastructure Setup

### 1. Database & Schema Structure

```sql
create database if not exists NYC_TAXI_DB;

create schema if not exists NYC_TAXI_DB.RAW;
create schema if not exists NYC_TAXI_DB.STAGING;
create schema if not exists NYC_TAXI_DB.FINAL;
```

---

### 2. Transformation Warehouse

```sql
create warehouse if not exists NYC_TAXI_WH
  warehouse_size = 'MEDIUM'
  auto_suspend = 60
  auto_resume = true;
```

---

### 3. Role Management & Permissions

```sql
-- Create role for dbt transformations
create role if not exists TRANSFORM;

-- Create dbt user
create user if not exists DBT
  password = 'Password123!'
  default_role = TRANSFORM
  default_warehouse = NYC_TAXI_WH
  must_change_password = true;

-- Assign role to user
grant role TRANSFORM to user DBT;
```

---

### 4. Granting Permissions

```sql
-- Warehouse privileges
grant usage, operate on warehouse NYC_TAXI_WH to role TRANSFORM;

-- Database access
grant usage on database NYC_TAXI_DB to role TRANSFORM;

-- Schema usage
grant usage on schema NYC_TAXI_DB.RAW to role TRANSFORM;
grant usage on schema NYC_TAXI_DB.STAGING to role TRANSFORM;
grant usage on schema NYC_TAXI_DB.FINAL to role TRANSFORM;

-- Read on RAW
grant select on all tables in schema NYC_TAXI_DB.RAW to role TRANSFORM;
grant select on future tables in schema NYC_TAXI_DB.RAW to role TRANSFORM;

-- Write on STAGING and FINAL
grant create table, create view on schema NYC_TAXI_DB.STAGING to role TRANSFORM;
grant create table, create view on schema NYC_TAXI_DB.FINAL to role TRANSFORM;
```

---

### 5. dbt Connection Profile

Sample `~/.dbt/profiles.yml`:

```yaml
nyc_taxi_dbt_snowflake:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <your_account>
      user: DBT
      password: <your_password>
      role: TRANSFORM
      database: NYC_TAXI_DB
      warehouse: NYC_TAXI_WH
      schema: STAGING
      threads: 1
      client_session_keep_alive: False
```

> ⚠️ Replace `<your_account>` and `<your_password>` accordingly. Secrets are stored in `.env` and accessed securely.

---

## ✅ Status

✅ Workstation is configured for industrial data engineering workflows.  
✅ Snowflake infrastructure is fully provisioned with dedicated role and security scopes.  
✅ dbt and CLI-based workflows are enabled for production-grade data transformations.