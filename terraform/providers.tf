terraform {
  required_providers {
    snowflake = {
      source  = "Snowflakedb/snowflake"
      version = "2.10.1"
    }
  }

  required_version = ">= 1.7.0"
}

provider "snowflake" {
  account_name = var.account
  organization_name = var.organization
  user = var.username
  password = var.password
  role     = var.role
  preview_features_enabled = ["snowflake_table_resource"]
}
