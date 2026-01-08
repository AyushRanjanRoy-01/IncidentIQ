"""Prometheus metrics instrumentation."""

from prometheus_client import Counter, Histogram, Gauge
from typing import Optional

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Alert metrics
alerts_ingested_total = Counter(
    'alerts_ingested_total',
    'Total alerts ingested',
    ['severity', 'service']
)

alerts_active = Gauge(
    'alerts_active',
    'Active alerts',
    ['service']
)

# Incident metrics
incidents_created_total = Counter(
    'incidents_created_total',
    'Total incidents created',
    ['service']
)

incidents_resolved_total = Counter(
    'incidents_resolved_total',
    'Total incidents resolved',
    ['service']
)

incident_resolution_time_seconds = Histogram(
    'incident_resolution_time_seconds',
    'Time to resolve incident',
    ['service']
)

# Agent metrics
agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_type']
)

agent_errors_total = Counter(
    'agent_errors_total',
    'Total agent errors',
    ['agent_type']
)

# Remediation metrics
remediation_actions_total = Counter(
    'remediation_actions_total',
    'Total remediation actions',
    ['action_type', 'status']
)

remediation_success_rate = Gauge(
    'remediation_success_rate',
    'Remediation success rate'
)

# TODO: Add record methods for each metric
