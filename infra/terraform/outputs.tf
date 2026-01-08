# Terraform outputs

output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = module.gke.cluster_name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = module.gke.cluster_endpoint
  sensitive   = true
}

output "postgres_instance_name" {
  description = "Cloud SQL instance name"
  value       = module.postgres.instance_name
}

output "redis_instance_name" {
  description = "Memorystore instance name"
  value       = module.redis.instance_name
}

# TODO: Add more outputs as needed
