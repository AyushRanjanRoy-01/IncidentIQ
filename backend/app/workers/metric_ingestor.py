"""Background worker for metric ingestion."""

from typing import Any


class MetricIngestor:
    """Background worker for ingesting metrics."""

    def __init__(self) -> None:
        """Initialize metric ingestor."""
        # TODO: Initialize Prometheus client
        pass

    async def run(self) -> None:
        """Run metric ingestor continuously.

        TODO: Poll Prometheus for new metrics
        TODO: Store in database
        TODO: Trigger anomaly detection
        """
        pass

    async def ingest_metric_batch(self, metrics: list[dict[str, Any]]) -> None:
        """Ingest batch of metrics.

        Args:
            metrics: List of metrics
        """
        # TODO: Store metrics in database
        pass
