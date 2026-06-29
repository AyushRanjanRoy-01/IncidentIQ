# IncidentIQ — Onboarding & Go-Live Guide

This guide takes a new operator from a fresh deploy to **connected to live systems
and handling real incidents**. Budget ~30–45 minutes.

> 🔒 **Golden rule:** keep the human-in-the-loop approval gate on, and connect
> **staging before production**. In live mode, an approved remediation really does
> restart / scale / roll back your workloads.

---

## Prerequisites

- A deployed IncidentIQ instance (see the deploy options in the README).
- Managed **PostgreSQL** and **Redis** endpoints.
- Admin access to the systems you want to connect (Kubernetes, Slack, etc.).
- The repo checked out locally so you can run the helper scripts.

---

## Step 1 — Secure the instance (5 min)

In your `.env` (start from [`.env.production.example`](../.env.production.example)):

```bash
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))")
SEED_DEMO_USERS=false                      # turn OFF the demo backdoor accounts
CORS_ORIGINS=https://incidentiq.yourco.com # your real frontend origin
```

Create your real admin (replaces the demo users):

```bash
python scripts/create_admin.py --username you --role admin --email you@yourco.com
```

## Step 2 — Database (5 min)

Point at managed Postgres and apply the schema:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/incidentiq
REDIS_URL=redis://redis-host:6379/0

cd backend && alembic upgrade head     # creates all tables
```

## Step 3 — Go live (flip the master switch)

```bash
INTEGRATIONS_MOCK_MODE=false
```

Everything below is now **real**. Configure only the integrations you want; each one
is independent and reports its own status.

---

## Step 4 — Connect your systems

### 🔭 Prometheus (metric context for RCA)
```bash
PROMETHEUS_URL=http://prometheus.monitoring.svc:9090
```
Read-only; just needs network reachability from the backend.

### ☸️ Kubernetes (self-healing: restart / scale / rollback)
```bash
KUBERNETES_ENABLED=true
KUBERNETES_NAMESPACE=production
pip install -r backend/requirements-optional.txt   # installs the kubernetes client
```
Give the backend **least-privilege** access. If running in-cluster, apply this
ServiceAccount + Role (scope to the namespaces you intend to manage):

```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: incidentiq, namespace: production }
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: incidentiq-remediator, namespace: production }
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "deployments/scale", "replicasets"]
    verbs: ["get", "list", "patch", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: incidentiq-remediator, namespace: production }
subjects: [{ kind: ServiceAccount, name: incidentiq, namespace: production }]
roleRef: { kind: Role, name: incidentiq-remediator, apiGroup: rbac.authorization.k8s.io }
```
Run the backend pod with `serviceAccountName: incidentiq`. (Locally, it falls back
to your `~/.kube/config`.)

### 💬 Slack (approval notifications)
1. Create a Slack app → **OAuth & Permissions** → add bot scope `chat:write`.
2. Install to your workspace, copy the **Bot User OAuth Token** (`xoxb-…`).
3. Invite the bot to the channel: `/invite @IncidentIQ`.
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#sre
```

### 📟 PagerDuty (paging on critical incidents)
1. In a PagerDuty service → **Integrations** → add an **Events API v2** integration.
2. Copy the **Integration/Routing Key**.
```bash
PAGERDUTY_ROUTING_KEY=...
```

### 🐙 GitHub (recent-deployment context)
1. Create a fine-grained PAT with **read-only** access to the repo (Deployments + Contents).
```bash
GITHUB_TOKEN=ghp_...
GITHUB_REPO=your-org/your-service
```

### 🧠 OpenAI (optional — upgrades RCA quality)
```bash
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```
Without a key, the deterministic engine is used — everything still works.

---

## Step 5 — Validate every connection ✅

Restart the backend so it picks up the new env, then:

```bash
python scripts/check_integrations.py
```
```
Integration mode: LIVE
  [ OK ]  kubernetes  (live)  12 deployments in production
  [ OK ]  prometheus  (live)  http://prometheus… (200)
  [ OK ]  slack       (live)  team=YourCo
  [ OK ]  github      (live)  login=incidentiq-bot
  [ OK ]  pagerduty   (live)  routing key present
  [FAIL]  terraform   (live)  terraform CLI not on PATH
```
Or hit the API (admin token): `GET /api/v1/integrations/status`. Fix anything red
before relying on it.

## Step 6 — Your first real incident

Point your alerting at IncidentIQ, or send one yourself:

```bash
curl -X POST https://incidentiq.yourco.com/api/v1/alerts/ingest \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"service":"checkout-api","severity":"critical","metric":"api_latency_p95","value":2500,"threshold":1000,"labels":{"env":"production"}}'
```

Then in the dashboard:
1. Open the incident → review the **RCA + recommended action + confidence**.
2. If it looks right, click **Approve** → IncidentIQ executes the fix and posts to Slack.
3. Watch the incident move to `remediating` → `resolved`.

> Connecting Alertmanager: post to `/api/v1/alerts/ingest` from an Alertmanager
> webhook receiver (a thin field mapping). A native Alertmanager adapter is on the
> roadmap — see [PRODUCTIZATION.md](./PRODUCTIZATION.md).

---

## Recommended rollout

1. **Staging, mock off, read-only integrations** (Prometheus/GitHub/Slack) — verify RCA quality.
2. **Staging Kubernetes** — approve a few restarts/scales/rollbacks manually.
3. **Production, approval required** — operators approve every action.
4. Only consider auto-execute for low-risk actions once you trust the confidence scores.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `check_integrations` shows `mock` | `INTEGRATIONS_MOCK_MODE` is still `true` |
| Slack `not configured` | `SLACK_BOT_TOKEN` unset, or bot not invited to the channel |
| K8s action fails | Check the ServiceAccount RBAC and `KUBERNETES_NAMESPACE` |
| Rollback fails "no previous revision" | The deployment has no prior ReplicaSet to revert to |
| 401 on every call | Wrong/expired JWT — log in again |
| 403 approving a fix | You need the `operator` or `admin` role |
