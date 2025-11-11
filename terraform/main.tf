resource "snowflake_database" "nyc_taxi_db" {
  name = "NYC_TAXI_DB_V2"
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.nyc_taxi_db.name
  name     = "RAW"
}

resource "snowflake_schema" "staging" {
  database = snowflake_database.nyc_taxi_db.name
  name     = "STAGING"
}

resource "snowflake_schema" "final" {
  database = snowflake_database.nyc_taxi_db.name
  name     = "FINAL"
}

resource "snowflake_warehouse" "nyc_taxi_wh" {
  name                = "NYC_TAXI_WH_V2"
  warehouse_size      = "MEDIUM"
  auto_suspend        = 60
  auto_resume         = true
  initially_suspended = true
}
