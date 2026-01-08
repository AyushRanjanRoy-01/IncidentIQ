# Redis Memorystore module

resource "google_redis_instance" "cache" {
  name           = var.instance_name
  memory_size_gb = var.memory_size_gb
  region         = var.region
  tier           = var.tier

  # TODO: Configure version
  # TODO: Set up auth
  # TODO: Configure persistence
}

variable "instance_name" {
  description = "Redis instance name"
  type        = string
}

variable "memory_size_gb" {
  description = "Memory size in GB"
  type        = number
  default     = 4
}

variable "tier" {
  description = "Service tier (basic or standard)"
  type        = string
  default     = "basic"
}

variable "region" {
  description = "GCP region"
  type        = string
}
