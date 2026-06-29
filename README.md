# IncidentIQ — AI-SRE Platform

AI-powered Site Reliability Engineering platform that ingests alerts, correlates
them into incidents, runs a **multi-agent root-cause analysis**, and proposes
**human-approved self-healing** remediations.

> **Runs with zero external accounts.** Out of the box it uses SQLite, an
> in-process cache, a deterministic offline LLM, and mock integrations — so you
> can `pip install` and have the full alert → incident → RCA → remediation flow
> working in minutes. Plug in PostgreSQL, OpenAI, Kubernetes, Slack, etc. by
> setting environment variables.

---

## Implementation status

This repository contains a **fully working vertical slice** plus the scaffolding
for a broader platform. Be aware of what is real vs. illustrative:

| Area | Status |
|------|--------|
| Auth (JWT + RBAC: viewer/operator/admin) | ✅ Implemented + tested |
| Alert ingestion, dedup fingerprinting, correlation | ✅ Implemented + tested |
| Incident lifecycle + persistence (SQLAlchemy 2.0 async) | ✅ Implemented + tested |
| Multi-agent RCA (triage → context → knowledge/RAG → RCA → supervisor) | ✅ Implemented + tested |
| RAG knowledge base (chunk + embed + cosine search over runbooks) | ✅ Implemented + tested |
| Self-healing remediation + human-in-the-loop approval | ✅ Implemented + tested |
| OpenAI LLM path (auto-enabled when `OPENAI_API_KEY` is set) | ✅ Implemented (falls back to deterministic mock) |
| Observability: structured logs, Prometheus `/metrics`, request IDs | ✅ Implemented |
| REST API + OpenAPI docs (`/docs`) | ✅ Implemented |
| React dashboard (login, incidents, RCA, approve/reject, knowledge search) | ✅ Implemented (build via Docker/Node 20) |
| CI (GitHub Actions: lint, tests, frontend build, image build) | ✅ Implemented |
| Alembic migrations (SQLite + PostgreSQL) | ✅ Implemented |
| External integrations (K8s, Prometheus, Slack, PagerDuty, GitHub, Terraform) | ⚠️ Mock-mode adapters; real branches stubbed behind flags |
| Background workers, ML anomaly detection, Kafka/Vault | 🧱 Scaffolded stubs (not part of the runnable slice) |

The 28-test suite exercises the end-to-end flow (`backend/tests`).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Ingestion Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Prometheus│  │   Loki   │  │  OTel    │  │  Kafka   │      │
│  │ Metrics  │  │  Logs    │  │ Traces   │  │  Events  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┴─────────────┴─────────────┘──────────────┘
        ▼
   ┌─────────────────────────────────────┐
   │      AI Intelligence Core            │
   │  Triage → Context → Knowledge (RAG)  │
   │            → RCA → Supervisor        │
   └──────────────┬──────────────────────┘
                  ▼
   ┌─────────────────────────────────────┐
   │   Remediation + Human Approval (HITL)│
   │   restart / scale / rollback / IaC   │
   └─────────────────────────────────────┘
```

## Tech stack

**Backend (core, lean & always installed):** FastAPI · SQLAlchemy 2.0 async ·
SQLite/PostgreSQL · Alembic · PyJWT · numpy (RAG) · structlog ·
prometheus-client · OpenAI SDK (optional at runtime).

**Backend (optional extras, see `backend/requirements-optional.txt`):** LangGraph ·
scikit-learn/Prophet · Kubernetes · Kafka · Vault · sentence-transformers ·
OpenTelemetry.

**Frontend:** React 18 · TypeScript · Vite · Tailwind v4 · TanStack Query · Zustand.

**Infra:** Docker · docker-compose · Terraform · Kubernetes/Helm · Prometheus + Grafana.

## Quick start

### Prerequisites
- Python 3.11+ (3.12 recommended)
- Docker & Docker Compose (for the full stack)
- Node 20+ (only to build the frontend natively; otherwise use Docker)

### Option A — Backend only, locally (fastest)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate   •   Linux/macOS: source venv/bin/activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

On startup the app creates the schema (SQLite), seeds demo users, and indexes the
sample runbooks. Then:

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

Drive the demo flow:

```bash
python ../scripts/simulate_alerts.py 5      # ingest alerts -> incidents -> RCA
```

### Option B — Full stack with Docker Compose

```bash
cp .env.example .env          # optional; sensible defaults work as-is
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API / docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 · Prometheus: http://localhost:9090

### Demo credentials

| User | Password | Role |
|------|----------|------|
| `admin` | `admin123` | admin |
| `operator` | `operator123` | operator (can ingest/approve) |
| `viewer` | `viewer123` | viewer (read-only) |

### Enabling the real LLM

Set `OPENAI_API_KEY` (and optionally `LLM_MODEL`, default `gpt-4o-mini`). The RCA
agent automatically uses OpenAI and falls back to the deterministic engine if the
call fails. With no key, everything still works using the offline engine.

## The end-to-end flow

1. `POST /api/v1/alerts/ingest` — an alert is stored, fingerprinted, and correlated
   to an active incident for its service (or a new one is created).
2. The supervisor runs **triage → context → knowledge (RAG) → RCA**, producing a
   root cause, confidence, and a recommended action.
3. If confidence ≥ `RCA_AUTO_PROPOSE_THRESHOLD` a remediation is auto-proposed in
   `pending_approval` (human-in-the-loop).
4. An operator approves via `POST /api/v1/remediation/{id}/approve`; the executor
   runs the action (mock by default) and the incident moves to `remediating`.

## Project structure

```
IncidentIQ/
├── backend/
│   ├── app/
│   │   ├── agents/        # multi-agent RCA pipeline + LLM provider
│   │   ├── api/           # FastAPI routers + middleware
│   │   ├── core/          # config + exceptions
│   │   ├── db/            # async engine + Alembic migrations
│   │   ├── integrations/  # mockable external system adapters
│   │   ├── models/        # SQLAlchemy models + Pydantic schemas + enums
│   │   ├── observability/ # logging, metrics, tracing
│   │   ├── rag/           # embeddings, chunker, vector store, retriever
│   │   ├── remediation/   # executor + actions + approval flow
│   │   ├── security/      # JWT auth, RBAC, rate limiting, validation
│   │   └── services/      # business logic (alert/incident/remediation/knowledge)
│   ├── data/              # sample runbooks, postmortems, alerts
│   └── tests/             # pytest suite (end-to-end + unit)
├── frontend/              # React + TypeScript dashboard
├── infra/                 # Terraform / Kubernetes / Helm
├── monitoring/            # Prometheus + Grafana config
└── scripts/               # seed_knowledge.py, simulate_alerts.py
```

## Development

```bash
# Backend
cd backend
ruff check . && black --check .     # lint + format
pytest --cov=app                    # tests
alembic upgrade head                # migrations (PostgreSQL)

# Frontend
cd frontend
npm ci
npm run typecheck                   # tsc (advisory)
npm run build                       # production build (Vite)
```

## License

MIT — see [CONTRIBUTING.md](./CONTRIBUTING.md) and [SECURITY.md](./SECURITY.md).
