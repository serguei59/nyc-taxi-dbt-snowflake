resource "snowflake_warehouse_grant" "warehouse_usage" {
  warehouse_name = snowflake_warehouse.nyc_taxi_wh.name
  privilege      = "USAGE"
  roles          = [snowflake_role.transform.name]
}

resource "snowflake_warehouse_grant" "warehouse_operate" {
  warehouse_name = snowflake_warehouse.nyc_taxi_wh.name
  privilege      = "OPERATE"
  roles          = [snowflake_role.transform.name]
}

resource "snowflake_database_grant" "db_usage" {
  database_name = snowflake_database.nyc_taxi_db.name
  privilege     = "USAGE"
  roles         = [snowflake_role.transform.name]
}

resource "snowflake_schema_grant" "schema_usage" {
  for_each = {
    raw     = snowflake_schema.raw.name
    staging = snowflake_schema.staging.name
    final   = snowflake_schema.final.name
  }
  database_name = snowflake_database.nyc_taxi_db.name
  schema_name   = each.value
  privilege     = "USAGE"
  roles         = [snowflake_role.transform.name]
}

# Grants for existing tables
resource "snowflake_table_grant" "raw_all" {
  database_name = var.database_name
  schema_name   = "RAW"
  privilege     = "ALL PRIVILEGES"
  roles         = [snowflake_role.transform.name]
  on_all        = true
}

resource "snowflake_table_grant" "staging_all" {
  database_name = var.database_name
  schema_name   = "STAGING"
  privilege     = "ALL PRIVILEGES"
  roles         = [snowflake_role.transform.name]
  on_all        = true
}

resource "snowflake_table_grant" "final_all" {
  database_name = var.database_name
  schema_name   = "FINAL"
  privilege     = "ALL PRIVILEGES"
  roles         = [snowflake_role.transform.name]
  on_all        = true
}

# Grants for future tables
resource "snowflake_future_table_grant" "raw_future" {
  database_name = var.database_name
  schema_name   = "RAW"
  privilege     = "ALL PRIVILEGES"
  roles         = [snowflake_role.transform.name]
}

resource "snowflake_future_table_grant" "staging_future" {
  database_name = var.database_name
  schema_name   = "STAGING"
  privilege     = "ALL PRIVILEGES"
  roles         = [snowflake_role.transform.name]
}

resource "snowflake_future_table_grant" "final_future" {
  database_name = var.database_name
  schema_name   = "FINAL"
  privilege     = "ALL PRIVILEGES"
  roles         = [snowflake_role.transform.name]
}
