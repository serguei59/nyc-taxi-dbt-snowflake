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

# --- Database & warehouse ---
variable "database" {
  description = "Nom de la base de données principale"
  type        = string
}

variable "warehouse" {
  description = "Nom du warehouse utilisé pour les transformations"
  type        = string
}

# --- Schémas ---
variable "schema" {
  description = "Liste des schémas à créer dans la base"
  type        = list(string)
}

variable "dbt_user_password" {
  description = "Password for DBT user"
  type        = string
  sensitive   = true
}
