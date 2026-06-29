# Validation Status

This document reflects the **actual, verified** state of the project (the previous
version overstated readiness).

## ✅ Verified working

### Backend — runs and is tested
```bash
cd backend
python -m venv venv && . venv/Scripts/activate   # or venv/bin/activate
pip install -r requirements-dev.txt
pytest                 # 28 tests pass (end-to-end + unit)
ruff check . && black --check .   # clean
uvicorn app.main:app   # boots, seeds users, indexes knowledge base
```

The test suite covers the full vertical slice:
- JWT login + RBAC enforcement (viewer/operator/admin)
- Alert ingestion → dedup/correlation → incident creation
- Multi-agent RCA (triage → context → knowledge/RAG → RCA → supervisor)
- Auto-proposed remediation + human approval → execution
- Knowledge base semantic search

A live `uvicorn` run was verified end-to-end over HTTP (login → ingest → incident
with RCA + recommended rollback at 0.95 confidence → approve → succeeded) with
Prometheus counters recording.

### Database
- Async SQLAlchemy 2.0 engine; SQLite by default, PostgreSQL via `DATABASE_URL`.
- Alembic initial migration generated and applied successfully.
- Tables auto-created on startup for zero-config local/dev.

### CI/CD
- `.github/workflows/ci.yml` runs: ruff + black + pytest (backend), `npm ci` +
  build (frontend), and Docker image builds for both services.

### Documentation
- `README.md` accurately describes implemented vs. mock vs. scaffolded areas.
- `.env.example` documents every setting (and is referenced by `make setup-local`).

## ⚠️ Mock-mode (works, but simulated)

External integrations run in **mock mode** by default and return realistic
synthetic results, so the self-healing flow is demonstrable without real systems:
- Kubernetes (restart/scale/rollback), Prometheus, GitHub, Slack, PagerDuty, Terraform.

Enable real behaviour with the relevant env flags + `requirements-optional.txt`
dependencies (`KUBERNETES_ENABLED=true`, `INTEGRATIONS_MOCK_MODE=false`, tokens, etc.).

The OpenAI LLM path is real and auto-enabled when `OPENAI_API_KEY` is set; without
a key the deterministic offline engine is used.

## 🧱 Scaffolded (not part of the runnable slice)

These remain structured stubs for future work and are **not** required for the
platform to run:
- Background workers (`app/workers/*`)
- ML anomaly detection / forecasting (`app/ml/*`)
- Kafka event streaming, Vault, feature flags, cost trackers

## Frontend

- React + TypeScript SPA wired to the API (login, dashboard, incident detail with
  RCA + approve/reject, knowledge search).
- Built with Vite; type-checking is available via `npm run typecheck` (advisory).
- Verified to build via the CI `frontend` job and the Docker image build.

## Summary

| Component | Structure | Implementation | Tested | Runnable |
|-----------|-----------|----------------|--------|----------|
| Backend (vertical slice) | ✅ | ✅ | ✅ 28 tests | ✅ |
| Database + migrations | ✅ | ✅ | ✅ | ✅ |
| Frontend | ✅ | ✅ | build-checked | ✅ (Docker/Node) |
| CI/CD | ✅ | ✅ | — | ✅ |
| External integrations | ✅ | ⚠️ mock-mode | ✅ (mock) | ✅ |
| Workers / ML / streaming | ✅ | 🧱 stub | — | — |
