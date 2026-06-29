<div align="center">

# 🛡️ IncidentIQ

### AI-powered Site Reliability Engineering — from alert to fix, automatically.

IncidentIQ ingests production alerts, correlates them into incidents, runs a
**multi-agent root-cause analysis**, and proposes a **human-approved self-healing**
action — so on-call engineers spend minutes, not hours, on every incident.

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Tests](https://img.shields.io/badge/tests-28%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
[![CI](https://github.com/AyushRanjanRoy-01/IncidentIQ/actions/workflows/ci.yml/badge.svg)](https://github.com/AyushRanjanRoy-01/IncidentIQ/actions/workflows/ci.yml)

</div>

---

## ⚡ Get running in one command

> **No database to install. No migrations to run. No API keys required.**
> The backend creates its own schema, seeds demo users, and indexes the sample
> knowledge base on startup. Everything heavy lives behind the backend.

```bash
git clone https://github.com/AyushRanjanRoy-01/IncidentIQ.git
cd IncidentIQ
docker compose up --build
```

Then open **http://localhost:3000** and log in with `operator` / `operator123`.

| Service | URL |
|---|---|
| 🖥️ Dashboard (frontend) | http://localhost:3000 |
| 📚 API docs (Swagger) | http://localhost:8000/docs |
| 📈 Grafana | http://localhost:3001 |
| 🔭 Prometheus | http://localhost:9090 |

That's it. Want to see incidents flow in automatically?

```bash
python scripts/simulate_alerts.py 5     # fires 5 alerts → incidents → RCA
```

---

## 👥 Who is this for?

| You are… | IncidentIQ helps you… |
|---|---|
| **SRE / DevOps / On-call engineer** | Cut MTTR — get an instant root-cause hypothesis + a ready-to-approve fix instead of digging through dashboards. |
| **Platform / Infra team** | A reference design for safe automated remediation with **human-in-the-loop** approval and a full audit trail. |
| **Engineering manager** | Fewer 3am pages, consistent incident handling, and metrics on remediation success. |
| **Developer learning modern AI systems** | A clean, working example of **multi-agent orchestration + RAG + FastAPI + async SQLAlchemy** you can read end-to-end. |
| **Hiring manager / reviewer** | A production-shaped project: auth/RBAC, tests, CI, observability, migrations, Docker — not just a notebook. |

---

## ✨ Key features

- 🤖 **Multi-agent RCA** — Triage → Context → Knowledge (RAG) → RCA → Supervisor.
- 🧠 **RAG over your runbooks & postmortems** — retrieves the right playbook for each alert.
- 🛠️ **Self-healing with guardrails** — restart / scale / rollback / IaC, gated by **human approval**.
- 🔌 **Runs offline or with OpenAI** — deterministic engine by default; set `OPENAI_API_KEY` to upgrade RCA.
- 🔐 **Auth & RBAC** — JWT with `viewer` / `operator` / `admin` roles.
- 📈 **Observability built in** — structured JSON logs, Prometheus `/metrics`, request IDs.
- 🧪 **Tested & CI'd** — 28-test suite, ruff + black, GitHub Actions.

---

## 🏗️ Architecture

> GitHub renders these Mermaid diagrams automatically.

```mermaid
flowchart TB
    PM["Prometheus / Alert sources"]
    UI["React SPA · Dashboard · Incidents · RCA · Approvals"]

    subgraph BE["Backend — FastAPI"]
        API["REST API + JWT Auth / RBAC"]
        SVC["Services: alert · incident · remediation · knowledge"]
        subgraph AG["Multi-Agent RCA pipeline"]
            direction LR
            TRI["Triage"] --> CTX["Context"] --> KNO["Knowledge / RAG"] --> RCA["RCA"] --> SUP["Supervisor"]
        end
        REM["Remediation Executor + Human approval"]
        LLM["LLM Provider: OpenAI or offline mock"]
    end

    subgraph DATA["State & Knowledge"]
        PG[("PostgreSQL")]
        RED[("Redis cache")]
        VEC[["Vector store: chunks + embeddings"]]
    end

    subgraph EXT["Integrations — mock-mode by default"]
        K8S["Kubernetes"]
        CHAT["Slack / PagerDuty"]
        TF["Terraform"]
    end

    PM -->|alerts| API
    UI <-->|JSON + JWT| API
    API --> SVC
    SVC --> TRI
    RCA --> LLM
    KNO --> VEC
    SVC --> PG
    SVC --> RED
    SUP --> REM
    REM --> K8S
    REM --> TF
    REM -->|notify| CHAT
```

### How an incident flows

```mermaid
sequenceDiagram
    autonumber
    participant Src as Alert source
    participant API as FastAPI
    participant SVC as Services
    participant AG as Agent pipeline
    participant KB as Knowledge (RAG)
    participant DB as Database
    participant OP as Operator
    participant SYS as Target system

    Src->>API: POST /alerts/ingest (JWT)
    API->>SVC: fingerprint + correlate
    SVC->>DB: upsert alert → incident
    SVC->>AG: analyze(incident)
    AG->>KB: retrieve relevant runbooks
    AG->>AG: triage → context → RCA
    AG-->>SVC: root cause + action + confidence
    SVC->>DB: store RCA, propose fix (pending_approval)
    Note over OP: Human-in-the-loop
    OP->>API: POST /remediation/{id}/approve
    API->>SYS: execute action (mock by default)
    SYS-->>API: success
    API->>DB: status = succeeded
```

### Incident lifecycle

```mermaid
stateDiagram-v2
    [*] --> open
    open --> analyzing: agents run
    analyzing --> awaiting_approval: confidence above threshold
    analyzing --> open: low confidence
    awaiting_approval --> remediating: operator approves
    awaiting_approval --> open: operator rejects
    remediating --> resolved: verified
    resolved --> [*]
```

---

## 🚀 Setup options

### Option A — Full stack (recommended, one command)

```bash
docker compose up --build
```

Brings up Postgres, Redis, the API, the dashboard, Prometheus, and Grafana. Zero
config — the bundled `.env` defaults work out of the box.

### Option B — Backend only, locally (no Docker)

Great for poking the API or running tests.

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate    |    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt     # runtime only (use requirements-dev.txt for tests)
uvicorn app.main:app --reload
```

On first start it auto-creates the SQLite DB, seeds demo users, and indexes the
sample runbooks. Open http://localhost:8000/docs.

### 🔑 Demo credentials

| User | Password | Can do |
|---|---|---|
| `admin` | `admin123` | Everything |
| `operator` | `operator123` | Ingest alerts, approve/reject fixes |
| `viewer` | `viewer123` | Read-only |

---

## 💡 Usage tips

**Drive the demo flow from the CLI**
```bash
python scripts/simulate_alerts.py 8        # generate incidents
python scripts/seed_knowledge.py           # (re)index runbooks/postmortems
```

**Walk the API by hand (curl)**
```bash
# 1) Log in
TOKEN=$(curl -s -X POST localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"operator","password":"operator123"}' | jq -r .access_token)

# 2) Ingest an alert → creates an incident + runs RCA
curl -s -X POST localhost:8000/api/v1/alerts/ingest \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"service":"checkout-api","severity":"critical","metric":"api_latency_p95","value":2500,"threshold":1000,"labels":{"env":"production"}}'

# 3) Inspect incidents, then approve the proposed fix in the dashboard or via:
#    POST /api/v1/remediation/{id}/approve
```

**Upgrade RCA to a real LLM** — set `OPENAI_API_KEY` (optionally `LLM_MODEL`,
default `gpt-4o-mini`). It auto-activates and falls back to the offline engine if a
call fails. No key? Everything still works.

**Add your own runbooks** — drop Markdown files in `backend/data/runbooks/` (or
`postmortems/`) and run `python scripts/seed_knowledge.py`. They become instantly
searchable and feed the RCA agent.

**Point at PostgreSQL** — set `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db`.

---

## ⚙️ Configuration

Everything is env-driven (see [`.env.example`](./.env.example)). The most useful knobs:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | SQLite file | Swap to PostgreSQL in production |
| `OPENAI_API_KEY` | _(unset)_ | Enables the real LLM RCA path |
| `LLM_PROVIDER` | `auto` | `auto` \| `openai` \| `mock` |
| `RCA_AUTO_PROPOSE_THRESHOLD` | `0.6` | Min confidence to auto-propose a fix |
| `INTEGRATIONS_MOCK_MODE` | `true` | Simulate K8s/Slack/etc. without real systems |
| `JWT_SECRET_KEY` | dev value | **Change in production** |
| `SEED_DEMO_USERS` | `true` | **Set `false` in production** |
| `CORS_ORIGINS` | `*` | Restrict to your frontend origin in production |

---

## 🧰 Tech stack

**Backend** FastAPI · async SQLAlchemy 2.0 · SQLite/PostgreSQL · Alembic · PyJWT ·
numpy (RAG) · structlog · Prometheus · OpenAI SDK (optional)
**Frontend** React 18 · TypeScript · Vite · Tailwind v4 · TanStack Query · Zustand
**Infra** Docker · docker-compose · Terraform · Kubernetes/Helm · Prometheus + Grafana

Heavy/optional capabilities (LangGraph, scikit-learn/Prophet, Kubernetes client,
Kafka, Vault, sentence-transformers, OpenTelemetry) live in
[`backend/requirements-optional.txt`](./backend/requirements-optional.txt) so the
core stays lean.

---

## 🗂️ Project structure

```
IncidentIQ/
├── backend/
│   └── app/
│       ├── agents/        # multi-agent RCA pipeline + LLM provider
│       ├── api/           # FastAPI routers + middleware
│       ├── core/          # config + exceptions
│       ├── db/            # async engine + Alembic migrations
│       ├── integrations/  # mockable external system adapters
│       ├── models/        # SQLAlchemy models + Pydantic schemas + enums
│       ├── observability/ # logging, metrics, tracing
│       ├── rag/           # embeddings, chunker, vector store, retriever
│       ├── remediation/   # executor + actions + approval flow
│       ├── security/      # JWT auth, RBAC, rate limiting, validation
│       └── services/      # business logic
├── frontend/              # React + TypeScript dashboard
├── infra/                 # Terraform / Kubernetes / Helm
├── monitoring/            # Prometheus + Grafana config
└── scripts/               # seed_knowledge.py, simulate_alerts.py
```

---

## 🧪 Development

```bash
cd backend
pip install -r requirements-dev.txt
ruff check . && black --check .     # lint + format
pytest --cov=app                    # 28 tests
```

```bash
cd frontend
npm ci && npm run build             # production build
npm run typecheck                   # tsc (advisory)
```

---

## 📊 What's real vs. scaffolded

See [VALIDATION_STATUS.md](./VALIDATION_STATUS.md) for the honest breakdown. In
short: the **alert → RCA → approved remediation** vertical slice is implemented and
tested; external integrations run in **mock mode** by default; background workers,
ML anomaly detection, and Kafka/Vault are structured stubs for future work.

## 🤝 Contributing & security

See [CONTRIBUTING.md](./CONTRIBUTING.md) and [SECURITY.md](./SECURITY.md).

## 📄 License

MIT.
