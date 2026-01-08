# Redis module variables

variable "instance_name" {
  description = "Redis instance name"
  type        = string
}

variable "memory_size_gb" {
  description = "Memory size in GB"
  type        = number
}

variable "tier" {
  description = "Service tier"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}
