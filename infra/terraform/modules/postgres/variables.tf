# PostgreSQL module variables

variable "instance_name" {
  description = "Cloud SQL instance name"
  type        = string
}

variable "database_name" {
  description = "Database name"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}
