# Development environment configuration

terraform {
  # TODO: Configure backend for dev
  # backend "gcs" {
  #   bucket = "terraform-state-dev"
  #   prefix = "ai-sre-platform"
  # }
}

# TODO: Reference modules with dev-specific values
# TODO: Set smaller resource sizes
# TODO: Disable HA for cost savings
