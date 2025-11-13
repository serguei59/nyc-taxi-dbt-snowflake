# ==========================================================
# Roles and Users
# ==========================================================

# Création du rôle TRANSFORM
resource "snowflake_account_role" "transform" {
  name = "TRANSFORM"
}

# Création de l'utilisateur DBT
resource "snowflake_user" "dbt_user" {
  name             = "DBT"
  password         = var.dbt_user_password
  default_role     = snowflake_account_role.transform.name
  default_warehouse = snowflake_warehouse.transform_wh.name
  must_change_password = true
}

# Attribution du rôle TRANSFORM à l'utilisateur DBT
resource "snowflake_grant_account_role" "grant_transform_to_dbt" {
  role_name = snowflake_account_role.transform.name
  user_name = snowflake_user.dbt_user.name

  depends_on = [
    snowflake_account_role.transform,
    snowflake_user.dbt_user
  ]
}
