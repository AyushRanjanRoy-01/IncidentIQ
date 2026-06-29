#!/usr/bin/env python3
"""Simulate alerts against a running IncidentIQ API.

Authenticates as the demo ``operator`` user, then POSTs randomised alerts to
``/api/v1/alerts/ingest`` — each triggers correlation + multi-agent RCA.

Usage:
    python scripts/simulate_alerts.py [count] [api_url]
    python scripts/simulate_alerts.py 5 http://localhost:8000
"""

import asyncio
import random
import sys
from datetime import datetime, timezone

import httpx

ALERT_TEMPLATES = [
    {"metric": "api_latency_p95", "threshold": 1000, "severity": "critical",
     "services": ["checkout-api", "payment-api", "user-api"]},
    {"metric": "error_rate", "threshold": 0.01, "severity": "warning",
     "services": ["checkout-api", "payment-api"]},
    {"metric": "cpu_usage", "threshold": 80, "severity": "warning",
     "services": ["checkout-api", "inventory-api"]},
    {"metric": "memory_usage", "threshold": 85, "severity": "critical",
     "services": ["user-api", "payment-api"]},
]


def _make_alert() -> dict:
    template = random.choice(ALERT_TEMPLATES)
    service = random.choice(template["services"])
    if template["metric"] == "error_rate":
        value = template["threshold"] * random.uniform(1.5, 5.0)
    else:
        value = template["threshold"] * random.uniform(1.1, 2.0)
    return {
        "alert_id": f"sim-{datetime.now().strftime('%H%M%S')}-{random.randint(1000, 9999)}",
        "severity": template["severity"],
        "service": service,
        "metric": template["metric"],
        "value": round(value, 2),
        "threshold": template["threshold"],
        "labels": {
            "env": random.choice(["production", "staging"]),
            "cluster": random.choice(["us-west-2", "us-east-1"]),
        },
        "fired_at": datetime.now(timezone.utc).isoformat(),
    }


async def main(count: int, api_url: str) -> None:
    async with httpx.AsyncClient(base_url=api_url, timeout=30.0) as client:
        login = await client.post(
            "/api/v1/auth/login", json={"username": "operator", "password": "operator123"}
        )
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print(f"Simulating {count} alert(s) against {api_url} ...")
        for _ in range(count):
            alert = _make_alert()
            resp = await client.post("/api/v1/alerts/ingest", json=alert, headers=headers)
            if resp.status_code == 201:
                body = resp.json()
                print(
                    f"  [{resp.status_code}] {alert['alert_id']} {alert['service']}/"
                    f"{alert['metric']} -> incident {body['incident_id']} "
                    f"(created={body['incident_created']})"
                )
            else:
                print(f"  [{resp.status_code}] failed: {resp.text[:120]}")
        print("Done.")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    asyncio.run(main(n, url))
