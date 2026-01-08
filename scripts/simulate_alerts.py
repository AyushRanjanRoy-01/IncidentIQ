#!/usr/bin/env python3
"""Simulate alerts for testing.

This script generates sample alerts to test the alert processing
and incident creation workflows.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import httpx


ALERT_TEMPLATES = [
    {
        "metric": "api_latency_p95",
        "threshold": 1000,
        "severity": "critical",
        "services": ["checkout-api", "payment-api", "user-api"],
    },
    {
        "metric": "error_rate",
        "threshold": 0.01,
        "severity": "warning",
        "services": ["checkout-api", "payment-api"],
    },
    {
        "metric": "cpu_usage",
        "threshold": 80,
        "severity": "warning",
        "services": ["checkout-api", "payment-api", "user-api", "inventory-api"],
    },
    {
        "metric": "memory_usage",
        "threshold": 85,
        "severity": "critical",
        "services": ["checkout-api", "payment-api"],
    },
]


async def simulate_alert(api_url: str = "http://localhost:8000"):
    """Simulate a single alert."""
    template = random.choice(ALERT_TEMPLATES)
    service = random.choice(template["services"])
    
    # Generate alert value above threshold
    if template["metric"] in ["api_latency_p95", "cpu_usage", "memory_usage"]:
        value = template["threshold"] * random.uniform(1.1, 2.0)
    else:  # error_rate
        value = template["threshold"] * random.uniform(1.5, 5.0)
    
    alert = {
        "alert_id": f"alert-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
        "severity": template["severity"],
        "service": service,
        "metric": template["metric"],
        "value": round(value, 2),
        "threshold": template["threshold"],
        "timestamp": datetime.utcnow().isoformat(),
        "labels": {
            "env": random.choice(["production", "staging"]),
            "cluster": random.choice(["us-west-2", "us-east-1"]),
        },
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_url}/api/v1/alerts",
                json=alert,
                timeout=10.0,
            )
            if response.status_code == 201:
                print(f"✅ Created alert: {alert['alert_id']} for {service}")
            else:
                print(f"❌ Failed to create alert: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating alert: {e}")


async def simulate_multiple_alerts(count: int = 5, api_url: str = "http://localhost:8000"):
    """Simulate multiple alerts."""
    print(f"🚨 Simulating {count} alerts...")
    
    tasks = [simulate_alert(api_url) for _ in range(count)]
    await asyncio.gather(*tasks)
    
    print("✅ Alert simulation complete!")


if __name__ == "__main__":
    import sys
    
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    asyncio.run(simulate_multiple_alerts(count, api_url))
