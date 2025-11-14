variable "account" {
  description = "Snowflake account identifier"
  type        = string
}

variable "organization" {
  description = "Snowflake account identifier"
  type        = string
}

variable "user" {
  description = "Snowflake admin username"
  type        = string
}

variable "password" {
  description = "Snowflake admin password"
  type        = string
  sensitive   = true
}

variable "role" {
  description = "Setup role"
  type        = string
}

variable "warehouse" {
  description = "Nom du warehouse utilisé pour les transformations"
  type        = string
}

variable "dbt_user_password" {
  description = "Password for DBT user"
  type        = string
  sensitive   = true
}
