# IAM roles and service accounts

# TODO: Create service accounts
# TODO: Define roles and permissions
# TODO: Configure workload identity
# TODO: Set up RBAC

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}
