# GKE module node pool configuration

resource "google_container_node_pool" "additional_pools" {
  name       = "additional-pool"
  location   = var.region
  cluster    = var.cluster_name
  node_count = var.node_count

  # TODO: Configure for specific workloads
  # TODO: Set up node affinity
  # TODO: Configure taints and tolerations
}
