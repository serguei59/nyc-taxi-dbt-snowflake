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
  must_change_password = false
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

# ==========================================================
# Rôle ANALYST — lecture seule sur FINAL
# ==========================================================

resource "snowflake_account_role" "analyst" {
  name = "ANALYST"
}

# LULU reçoit TRANSFORM (accès complet données) et ANALYST (démo lecture seule)
resource "snowflake_grant_account_role" "grant_transform_to_lulu" {
  role_name = snowflake_account_role.transform.name
  user_name = "LULU"

  depends_on = [snowflake_account_role.transform]
}

resource "snowflake_grant_account_role" "grant_analyst_to_lulu" {
  role_name = snowflake_account_role.analyst.name
  user_name = "LULU"

  depends_on = [snowflake_account_role.analyst]
}
