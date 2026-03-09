# ==========================================================
# GRANTS – Warehouse, Database, Schemas & Tables
# ==========================================================

# ✅ 1️⃣  Warehouse grants (USAGE, OPERATE)
resource "snowflake_grant_privileges_to_account_role" "warehouse_usage_operate" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["USAGE", "OPERATE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.transform_wh.name
  }

  depends_on = [
    snowflake_warehouse.transform_wh,
    snowflake_account_role.transform
  ]
}

# ✅ 2️⃣  Database usage grant
resource "snowflake_grant_privileges_to_account_role" "database_usage" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["USAGE", "CREATE SCHEMA"]

  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.nyc_taxi_db.name
  }

  depends_on = [
    snowflake_database.nyc_taxi_db,
    snowflake_account_role.transform
  ]
}

# ✅ 3️⃣  Schema grants (moindre privilège par schéma)

# RAW : lecture seule — l'ETL Python gère l'écriture
resource "snowflake_grant_privileges_to_account_role" "schema_raw_usage" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["USAGE"]

  on_schema {
    schema_name = "${snowflake_database.nyc_taxi_db.name}.RAW"
  }

  depends_on = [
    snowflake_schema.raw,
    snowflake_account_role.transform
  ]
}

# STAGING : dbt crée et remplace des tables/vues ici
resource "snowflake_grant_privileges_to_account_role" "schema_staging_usage" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]

  on_schema {
    schema_name = "${snowflake_database.nyc_taxi_db.name}.STAGING"
  }

  depends_on = [
    snowflake_schema.staging,
    snowflake_account_role.transform
  ]
}

# FINAL : dbt crée et remplace des tables/vues ici
resource "snowflake_grant_privileges_to_account_role" "schema_final_usage" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]

  on_schema {
    schema_name = "${snowflake_database.nyc_taxi_db.name}.FINAL"
  }

  depends_on = [
    snowflake_schema.final,
    snowflake_account_role.transform
  ]
}


##############################################
# GRANT ALL PRIVILEGES ON EXISTING TABLES
##############################################

# RAW — lecture seule pour TRANSFORM
resource "snowflake_grant_privileges_to_account_role" "raw_tables_existing" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["SELECT"]

  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.nyc_taxi_db.name}.RAW"
    }
  }

  depends_on = [
    snowflake_schema.raw,
    snowflake_account_role.transform
  ]
}

# STAGING
resource "snowflake_grant_privileges_to_account_role" "staging_tables_existing" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["ALL PRIVILEGES"]

  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.nyc_taxi_db.name}.STAGING"
    }
  }

  depends_on = [
    snowflake_schema.staging,
    snowflake_account_role.transform
  ]
}

# FINAL
resource "snowflake_grant_privileges_to_account_role" "final_tables_existing" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["ALL PRIVILEGES"]

  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.nyc_taxi_db.name}.FINAL"
    }
  }

  depends_on = [
    snowflake_schema.final,
    snowflake_account_role.transform
  ]
}

##############################################
# GRANT ALL PRIVILEGES ON FUTURE TABLES
##############################################

# RAW — lecture seule pour TRANSFORM
resource "snowflake_grant_privileges_to_account_role" "raw_tables_future" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["SELECT"]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.nyc_taxi_db.name}.RAW"
    }
  }

  depends_on = [
    snowflake_schema.raw,
    snowflake_account_role.transform
  ]
}

# STAGING
resource "snowflake_grant_privileges_to_account_role" "staging_tables_future" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["ALL PRIVILEGES"]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.nyc_taxi_db.name}.STAGING"
    }
  }

  depends_on = [
    snowflake_schema.staging,
    snowflake_account_role.transform
  ]
}

# FINAL
resource "snowflake_grant_privileges_to_account_role" "final_tables_future" {
  account_role_name = snowflake_account_role.transform.name
  privileges        = ["ALL PRIVILEGES"]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.nyc_taxi_db.name}.FINAL"
    }
  }

  depends_on = [
    snowflake_schema.final,
    snowflake_account_role.transform
  ]
}

# ==========================================================
# ✅ Résumé (moindre privilège) :
# - TRANSFORM reçoit :
#   - USAGE + OPERATE sur le warehouse
#   - USAGE + CREATE SCHEMA sur la database
#   - RAW    : USAGE schéma + SELECT tables (lecture source)
#   - STAGING: USAGE + CREATE TABLE + CREATE VIEW + ALL sur tables
#   - FINAL  : USAGE + CREATE TABLE + CREATE VIEW + ALL sur tables
# ==========================================================
