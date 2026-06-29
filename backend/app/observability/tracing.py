"""Distributed tracing setup (OpenTelemetry, optional).

No-op unless ``OTEL_ENABLED=true`` *and* the OpenTelemetry packages from
requirements-optional.txt are installed. This keeps the core runtime lean while
allowing full tracing in production by flipping a flag and installing the extras.
"""

from __future__ import annotations

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


def setup_tracing(app) -> None:
    """Instrument the FastAPI app with OTel when enabled; otherwise a no-op."""
    if not settings.otel_enabled:
        logger.debug("tracing.disabled")
        return
    try:  # pragma: no cover - optional dependency + collector required
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": settings.app_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint or None)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        logger.info("tracing.enabled", endpoint=settings.otel_exporter_otlp_endpoint)
    except Exception as exc:
        logger.warning("tracing.setup_failed", error=str(exc))
