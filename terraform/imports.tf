# ==========================================================
# IMPORTS – Ressources existantes dans Snowflake
# State perdu lors de la migration vers Terraform Cloud.
# Ces blocs permettent de ré-attacher le state aux ressources.
# ==========================================================

import {
  to = snowflake_warehouse.transform_wh
  id = "NYC_TAXI_WH_RNCP"
}

import {
  to = snowflake_account_role.transform
  id = "TRANSFORM"
}

import {
  to = snowflake_database.nyc_taxi_db
  id = "NYC_TAXI_DB_RNCP"
}

import {
  to = snowflake_schema.raw
  id = "NYC_TAXI_DB_RNCP.RAW"
}

import {
  to = snowflake_schema.staging
  id = "NYC_TAXI_DB_RNCP.STAGING"
}

import {
  to = snowflake_schema.final
  id = "NYC_TAXI_DB_RNCP.FINAL"
}

import {
  to = snowflake_user.dbt_user
  id = "DBT"
}

import {
  to = snowflake_table.raw_yellow_taxi_trips_v2
  id = "NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2"
}

import {
  to = snowflake_table.raw_buffer_yellow_taxi_trips_v2
  id = "NYC_TAXI_DB_RNCP.RAW.BUFFER_YELLOW_TAXI_TRIPS_V2"
}
