# GKE cluster module

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region
  
  # TODO: Configure node pool
  # TODO: Set cluster options
  # TODO: Configure networking
  # TODO: Configure security
  # TODO: Set up logging/monitoring
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.cluster_name}-node-pool"
  cluster    = google_container_cluster.primary.name
  node_count = var.node_count

  node_config {
    # TODO: Set machine type
    # TODO: Configure OAuth scopes
    # TODO: Set labels and metadata
    # TODO: Configure disk size
  }
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
}
