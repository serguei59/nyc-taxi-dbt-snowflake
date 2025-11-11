resource "snowflake_role" "transform" {
  name = "TRANSFORM"
}

resource "snowflake_user" "dbt" {
  name                 = "DBT"
  password             = var.dbt_password
  default_role         = snowflake_role.transform.name
  default_warehouse    = snowflake_warehouse.nyc_taxi_wh.name
  must_change_password = false
}

resource "snowflake_role_grants" "grant_transform_to_user" {
  role_name = snowflake_role.transform.name
  users     = [snowflake_user.dbt.name]
}
