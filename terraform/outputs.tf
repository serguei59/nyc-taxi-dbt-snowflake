output "snowflake_database" {
  value = snowflake_database.nyc_taxi_db.name
}

output "snowflake_user" {
  value = snowflake_user.dbt_user.name
}

output "snowflake_role" {
  value = snowflake_account_role.transform.name
}
