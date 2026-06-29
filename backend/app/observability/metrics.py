"""Prometheus metrics instrumentation."""

from prometheus_client import Counter, Gauge, Histogram

# Request metrics
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"]
)

# Alert metrics
alerts_ingested_total = Counter(
    "alerts_ingested_total", "Total alerts ingested", ["severity", "service"]
)

alerts_active = Gauge("alerts_active", "Active alerts", ["service"])

# Incident metrics
incidents_created_total = Counter("incidents_created_total", "Total incidents created", ["service"])

incidents_resolved_total = Counter(
    "incidents_resolved_total", "Total incidents resolved", ["service"]
)

incident_resolution_time_seconds = Histogram(
    "incident_resolution_time_seconds", "Time to resolve incident", ["service"]
)

# Agent metrics
agent_execution_duration_seconds = Histogram(
    "agent_execution_duration_seconds", "Agent execution duration", ["agent_type"]
)

agent_errors_total = Counter("agent_errors_total", "Total agent errors", ["agent_type"])

# Remediation metrics
remediation_actions_total = Counter(
    "remediation_actions_total", "Total remediation actions", ["action_type", "status"]
)

remediation_success_rate = Gauge("remediation_success_rate", "Remediation success rate")


# --------------------------------------------------------------------- helpers
def record_alert_ingested(severity: str, service: str) -> None:
    alerts_ingested_total.labels(severity=severity, service=service).inc()


def record_incident_created(service: str) -> None:
    incidents_created_total.labels(service=service).inc()


def record_remediation(action_type: str, status: str) -> None:
    remediation_actions_total.labels(action_type=action_type, status=status).inc()


# ------------------------------------------------------------------ middleware
import time  # noqa: E402

from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
from starlette.requests import Request  # noqa: E402


class MetricsMiddleware(BaseHTTPMiddleware):
    """Record per-request count and latency, labelled by route template."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        # Prefer the route path template (low cardinality) over the raw path.
        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        elapsed = time.perf_counter() - start
        http_requests_total.labels(
            method=request.method, endpoint=endpoint, status=str(response.status_code)
        ).inc()
        http_request_duration_seconds.labels(method=request.method, endpoint=endpoint).observe(
            elapsed
        )
        return response
