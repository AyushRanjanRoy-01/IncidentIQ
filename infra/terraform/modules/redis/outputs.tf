# Redis module outputs

output "host" {
  value = google_redis_instance.cache.host
}

output "port" {
  value = google_redis_instance.cache.port
}

output "connection_string" {
  value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
}
