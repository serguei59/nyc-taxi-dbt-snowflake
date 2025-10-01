
# ✅ Project Setup: NYC Yellow Taxi Data on Snowflake

This setup outlines the initial infrastructure and configuration steps to prepare the data platform for ingesting and modeling NYC Yellow Taxi data.

---

## 1. Snowflake Account Configuration

- **Account**: `CAHMYND-AO09940.snowflakecomputing.com`
- **Region**: `eu-west-3` (Paris AWS region)
- **Warehouse**: `COMPUTE_WH`
- **Database**: `NYC_TAXI`
- **Schema**: `RAW`
- **Role**: `ACCOUNTADMIN` (initial setup)

---

## 2. Roles and Privileges

### ❗ Role Management for Security

- **Default Role Used**: `ACCOUNTADMIN` (for setup only).
- **Best Practice**: Switch to a **custom role** with limited privileges for ingestion and modeling.

### 🔐 Minimal Role for dbt Usage

Create a new role for dbt interactions:

```sql
CREATE ROLE dbt_role;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE dbt_role;
GRANT USAGE ON DATABASE NYC_TAXI TO ROLE dbt_role;
GRANT USAGE ON SCHEMA NYC_TAXI.RAW TO ROLE dbt_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA NYC_TAXI.RAW TO ROLE dbt_role;
GRANT ROLE dbt_role TO USER your_user;
```

Set the user default role in Snowflake console or `ALTER USER`.

---

## 3. SnowSQL Installation

Installed via `.rpm` on Linux using:

```bash
sudo alien -d snowflake-snowsql-1.4.5-1.x86_64.rpm
sudo dpkg -i snowflake-snowsql_1.4.5-2_amd64.deb
```

Then configured using `~/.snowsql/config`.

---

## 4. dbt Core Setup

- Installed dbt Core via pip: `pip install dbt-snowflake`
- Created `.env` file with:

```
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
SNOWFLAKE_ACCOUNT=CAHMYND-AO09940
SNOWFLAKE_ROLE=dbt_role
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=NYC_TAXI
SNOWFLAKE_SCHEMA=RAW
```

- Created `~/.dbt/profiles.yml` (ignored by Git) using the same credentials.

---

## 5. dbt Project Initialized

```bash
dbt init nyc_taxi_dbt_snowflake
```

Created folder `nyc_taxi_dbt_snowflake/` containing:

- `dbt_project.yml`
- `models/`
- `macros/` (optional)
- Project now ready to receive transformations.

---

## ✅ Summary

The Snowflake infrastructure is ready for ingestion and modeling. dbt is fully configured to connect securely with a dedicated role and restricted access. All secrets are safely managed in the `.env` file.
