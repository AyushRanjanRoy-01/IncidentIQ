# PostgreSQL Cloud SQL module

resource "google_sql_database_instance" "postgres" {
  name             = var.instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  # TODO: Configure settings
  # TODO: Set up backups
  # TODO: Configure SSL
  # TODO: Set up replicas
}

resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres.name
}

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
