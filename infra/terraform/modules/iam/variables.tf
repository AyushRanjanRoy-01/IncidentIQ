# IAM module variables

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}
