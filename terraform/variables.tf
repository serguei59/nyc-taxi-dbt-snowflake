variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake admin username"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake admin password"
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "Setup role (ACCOUNTADMIN)"
  type        = string
  default     = "ACCOUNTADMIN"
}

variable "dbt_password" {
  description = "Password for DBT user"
  type        = string
  sensitive   = true
  default     = "Password123!"
}

variable "snowflake_warehouse" {}
variable "snowflake_database" {}
variable "snowflake_schema" {}