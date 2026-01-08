# Monitoring module for Prometheus and Grafana

# TODO: Set up Prometheus stack
# TODO: Configure alert rules
# TODO: Set up Grafana
# TODO: Configure service monitors

variable "namespace" {
  description = "Kubernetes namespace for monitoring"
  type        = string
  default     = "monitoring"
}
