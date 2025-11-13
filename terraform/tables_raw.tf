# ==========================================================
# RAW TABLES – NYC Taxi V2
# ==========================================================

locals {
  raw_columns = [
    "VENDOR_ID STRING",
    "PICKUP_DATETIME TIMESTAMP_NTZ",
    "DROPOFF_DATETIME TIMESTAMP_NTZ",
    "PASSENGER_COUNT INT",
    "TRIP_DISTANCE FLOAT",
    "RATE_CODE_ID INT",
    "STORE_AND_FWD_FLAG STRING",
    "PU_LOCATION_ID INT",
    "DO_LOCATION_ID INT",
    "PAYMENT_TYPE INT",
    "FARE_AMOUNT FLOAT",
    "EXTRA FLOAT",
    "MTA_TAX FLOAT",
    "TIP_AMOUNT FLOAT",
    "TOLLS_AMOUNT FLOAT",
    "IMPROVEMENT_SURCHARGE FLOAT",
    "TOTAL_AMOUNT FLOAT",
    "CONGESTION_SURCHARGE FLOAT",
    "AIRPORT_FEE FLOAT"
  ]
}

# -----------------------
# BUFFER_YELLOW_TAXI_TRIPS_V2
# -----------------------
resource "snowflake_table" "raw_buffer_yellow_taxi_trips_v2" {
  database = snowflake_database.nyc_taxi_db.name
  schema   = snowflake_schema.raw.name
  name     = "BUFFER_YELLOW_TAXI_TRIPS_V2"

  dynamic "column" {
    for_each = local.raw_columns
    content {
      name = split(" ", column.value)[0]
      type = split(" ", column.value)[1]
    }
  }
}

# -----------------------
# YELLOW_TAXI_TRIPS_V2
# -----------------------
resource "snowflake_table" "raw_yellow_taxi_trips_v2" {
  database = snowflake_database.nyc_taxi_db.name
  schema   = snowflake_schema.raw.name
  name     = "YELLOW_TAXI_TRIPS_V2"

  dynamic "column" {
    for_each = local.raw_columns
    content {
      name = split(" ", column.value)[0]
      type = split(" ", column.value)[1]
    }
  }
}
