resource "snowflake_database" "nyc_taxi_db" {
  name = "NYC_TAXI_DB_RNCP"
}

resource "snowflake_schema" "raw" {
  database          = snowflake_database.nyc_taxi_db.name
  name              = "RAW"
  is_transient      = "false"
  with_managed_access = "false"
}

resource "snowflake_schema" "staging" {
  database          = snowflake_database.nyc_taxi_db.name
  name              = "STAGING"
  is_transient      = "false"
  with_managed_access = "false"
}

resource "snowflake_schema" "final" {
  database          = snowflake_database.nyc_taxi_db.name
  name              = "FINAL"
  is_transient      = "false"
  with_managed_access = "false"
}

resource "snowflake_warehouse" "transform_wh" {
  name                      = "NYC_TAXI_WH_RNCP"
  warehouse_size            = "MEDIUM"
  auto_suspend              = 60
  auto_resume               = true
  initially_suspended       = true
  enable_query_acceleration = "false"
}
