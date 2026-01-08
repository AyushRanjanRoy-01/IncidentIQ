# Demo Scenarios

## Scenario 1: High API Latency Detection and Remediation

**Setup**: Deploy AI-SRE platform with sample services

**Step 1: Trigger Alert**
```bash
# Simulate high latency in checkout service
curl -X POST http://localhost:8000/api/v1/alerts/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "demo-001",
    "service": "checkout-api",
    "severity": "critical",
    "metric": "api_latency_p95",
    "value": 2500,
    "threshold": 1000,
    "timestamp": "2024-01-09T10:30:00Z"
  }'
```

**Step 2: Watch Dashboard**
- Frontend dashboard updates with alert in red
- Alert shows severity, service, and threshold violation

**Step 3: AI Analysis**
- Supervisor agent orchestrates all specialists in parallel
- Triage Agent: Validates alert is not a duplicate
- Context Agent: Gathers logs showing recent deployment
- Knowledge Agent: Retrieves "High Latency Runbook"
- RCA Agent: Synthesizes data → "Likely deployment regression"

**Step 4: RCA Display**
- Frontend shows RCA summary with 85% confidence
- Displays evidence from logs and metrics
- Suggests primary remediation: "Rollback Deployment"

**Step 5: Human Approval**
- Slack notification sent to #incidents channel
- Button: "[Approve Rollback] [View Debug Links] [Reject]"
- On-call engineer clicks [Approve Rollback]

**Step 6: Automatic Remediation**
- System executes Kubernetes rollback
- Monitors error rates and latency during rollback
- Sends confirmation to Slack: "✓ Rollback successful, metrics normalizing"

**Outcome**: Incident resolved in 5 minutes without human intervention

## Scenario 2: Database Connection Pool Exhaustion

**Step 1: Multiple Alert Trigger**
```bash
curl -X POST http://localhost:8000/api/v1/alerts/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "demo-002-1",
    "service": "database",
    "severity": "critical",
    "metric": "pg_connections_used_percent",
    "value": 95,
    "threshold": 80
  }'

curl -X POST http://localhost:8000/api/v1/alerts/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "demo-002-2",
    "service": "api-service",
    "severity": "high",
    "metric": "db_connection_errors",
    "value": 150,
    "threshold": 10
  }'
```

**Step 2: Alert Correlation**
- ML correlator groups related alerts
- Identifies root cause: database connection exhaustion
- Creates single incident instead of multiple

**Step 3: RCA Process**
- Context Agent pulls recent code changes (N+1 query commit)
- Knowledge Agent finds post-mortem from similar incident
- RCA Agent suggests: "Likely N+1 query in recent code"
- Confidence: 75%
- Primary action: Rollback (90% confidence)
- Secondary action: Increase pool size temporarily (60% confidence)

**Step 4: Approval & Execution**
- Slack shows primary recommendation with options
- On-call can approve primary or choose secondary
- System executes chosen remediation
- Monitors connection count in real-time

**Step 5: Post-Incident**
- Logs decision: rollback was successful
- Creates GitHub issue: "Investigate N+1 query in deploy v2.5.1"
- Stores incident data for future learning

## Scenario 3: Predictive Scaling Before Capacity Issue

**Background**: Weekend spike predicted based on historical patterns

**Step 1: Predictor Agent Triggers**
- Prophet model forecasts 3x traffic increase on Sunday
- Capacity planning agent predicts pod exhaustion by 2 PM

**Step 2: Proactive Action**
- System generates remediation: "Scale to 30 replicas"
- Confidence: 85% (high forecast accuracy)
- Sends notification: "Predictive scaling recommended for Sunday"

**Step 3: Human Review**
- On-call reviews forecast chart and historical patterns
- Approves proactive scaling

**Step 4: Automatic Execution**
- System scales deployment at 1 PM Sunday
- Adds extra capacity buffer
- Monitors metrics as traffic arrives

**Outcome**: Weekend spike handled without incident

## Scenario 4: Incident Playbook Discovery

**Situation**: Unfamiliar error: "PostgreSQL: WAL segment gone"

**Step 1: Alert Received**
- Error detected in logs, alert triggered
- AI agents begin analysis

**Step 2: Knowledge Retrieval**
- Knowledge agent searches: "WAL segment gone postgres"
- Retrieves: Post-mortem from incident on 2023-11-15
  - Included detailed troubleshooting steps
  - Root cause: Disk space exhaustion
  - Resolution: Increase disk size, increase wal_keep_size

**Step 3: RCA with Historical Context**
- RCA agent uses knowledge to inform analysis
- Confidence: 90% based on exact match to past incident
- Suggests: Increase disk size and adjust wal_keep_size

**Step 4: Execution**
- System could auto-remediate (if safe)
- Or present to on-call with confidence-based recommendation

**Outcome**: Resolved faster than first-time incident

## Key Demo Metrics

After running these scenarios:

| Metric | Target | Demo Result |
|--------|--------|-------------|
| Alert Ingestion Latency | < 100ms | ~50ms |
| RCA Generation Time | < 5 min | ~2 min |
| Remediation Execution | < 1 min | ~30s |
| End-to-End MTTR | < 10 min | ~5 min |
| AI Confidence Score | 80%+ | 75-90% |
| Human Approval Rate | 90%+ | 100% |
| Remediation Success | 95%+ | 100% |

## Interactive Demo Script

```bash
# 1. Open three terminals

# Terminal 1: Watch frontend
open http://localhost:3000

# Terminal 2: Watch backend logs
kubectl logs -f deployment/backend -n ai-sre

# Terminal 3: Send demo alerts
./scripts/simulate_alerts.py

# Or use makefile shortcut
make demo
```
