# From Project to Product — Gap Analysis & Roadmap

IncidentIQ today is a **working, single-tenant, self-hostable application** with a
real incident → RCA → approved-remediation flow and live integrations. This doc is
the honest list of what stands between that and a **product real customers pay for**,
organised by theme and then sequenced into phases.

> TL;DR: the *engine* is built. The work ahead is mostly **multi-tenancy, identity,
> secrets, safety guardrails, reliability, compliance, and self-serve onboarding** —
> i.e. the "-ilities" and commercial surface, not the core AI logic.

---

## Where we are vs. where a product needs to be

| Theme | Today | Needed for a product |
|---|---|---|
| **Tenancy** | Single tenant; one shared DB | Tenant model + row-level isolation (or DB-per-tenant), tenant-scoped everything |
| **Identity** | JWT + 3 static roles, password login | SSO (OIDC/SAML), SCIM provisioning, org/team/role hierarchy, API keys, audit of access |
| **Secrets** | Integration creds in env vars | Encrypted at rest, per-tenant secrets, Vault/KMS, rotation, no plaintext in logs |
| **Integrations** | K8s, Prometheus, Slack, PagerDuty, GitHub, Terraform (direct) | Native Alertmanager/Datadog/Grafana/Opsgenie, OAuth install flows, retries + circuit breakers, per-tenant config UI |
| **Reliability** | Single process; in-process cache + rate limit; inline RCA | Stateless HA replicas, durable job queue for RCA, distributed rate limiting, idempotency, timeouts/backpressure |
| **Safety of automation** | Human approval gate; mock by default | Blast-radius limits, dry-run/plan, change windows, approval policies, auto-rollback of failed remediations, per-action guardrails |
| **Data / RAG** | In-DB embeddings + numpy cosine | pgvector/managed vector DB at scale, ingestion pipeline for customer runbooks, feedback loop + RCA quality eval |
| **Observability (of the product)** | App logs + Prometheus metrics | SLOs/error budgets, distributed tracing, on-call + alerting on IncidentIQ itself, per-tenant usage metrics |
| **Security & compliance** | Basic auth, input validation, rate limit | Audit log, dependency/SAST/secret scanning, pen test, SOC 2 / ISO 27001, data retention & PII policy, DPA |
| **Onboarding / commercial** | Manual env + scripts | Self-serve signup, tenant provisioning, integration config UI, billing/metering, usage limits, plans |
| **Delivery** | Docker images + dev compose; Helm/Terraform scaffolds | Finished Helm chart, Terraform modules, versioned releases, zero-downtime migrations, blue/green |
| **Support** | README + onboarding doc | Status page, SLAs, in-app help, customer-facing docs site, support workflow |

---

## Phased roadmap

### Phase 0 — Done ✅
Single-tenant app: auth + RBAC, alert → incident → multi-agent RCA → approved
remediation, live integrations with connection validation, tests, CI, observability,
migrations, onboarding guide.

### Phase 1 — Production-grade for your first (self-hosted) customer · ~4–6 weeks
The minimum to run it for one real team in production.
- **Audit log** of every auth event, approval, and remediation (immutable, queryable).
- **Secrets hardening** — pull integration creds from a secret store (Vault/cloud KMS), encrypt at rest, scrub from logs.
- **Native Alertmanager adapter** (+ webhook signature verification) so existing alerting plugs in with zero glue.
- **Durable RCA execution** — move analysis to a background queue (the `workers/` package) so ingestion is fast and retried on failure.
- **HA**: run ≥2 stateless backend replicas → replace in-process rate limiting with Redis-backed; ensure idempotent ingestion.
- **Finish the Helm chart** + zero-downtime migration step; smoke-tested deploy.
- **Remediation guardrails**: dry-run mode, blast-radius caps (max pods/replicas), and auto-rollback when a fix doesn't improve the signal.

### Phase 2 — Multi-tenant SaaS foundations · ~2–3 months
What lets external customers self-serve.
- **Tenancy model** — `tenant_id` on every row + enforced row-level isolation; tenant-scoped knowledge bases, integrations, and users.
- **Enterprise identity** — OIDC/SAML SSO, SCIM, org→team→role hierarchy, scoped API keys.
- **Per-tenant integration config UI** (replace env vars) with OAuth install flows for Slack/GitHub/PagerDuty.
- **Billing & metering** — usage tracking (incidents/RCAs/LLM tokens), plans, limits, Stripe.
- **Self-serve onboarding** — signup → tenant provisioning → guided "connect your tools" wizard (built on the existing `/integrations/status` checks).

### Phase 3 — Scale, trust & growth · ongoing
- **Compliance**: SOC 2 Type II, pen test, vulnerability management, data residency & retention.
- **SRE the product**: SLOs/error budgets, tracing, alerting, capacity planning, multi-region.
- **RCA quality flywheel**: capture operator approve/reject + outcomes, evaluate and tune prompts/models, golden-set regression tests.
- **Integration marketplace**: Datadog, Grafana, Opsgenie, ServiceNow, Jira, cloud providers.
- **Advanced automation**: policy engine for when auto-execute is allowed; learned confidence thresholds per service.

---

## Smallest path to a first paying customer

If the goal is *one* design-partner customer fast, do a focused slice of Phase 1:
1. Audit log + secrets in a vault.
2. Native Alertmanager ingestion.
3. HA (2 replicas + Redis rate limiting) and durable RCA queue.
4. Remediation guardrails (dry-run + blast-radius cap).
5. Finished Helm chart + runbook.

That's a defensible, supportable single-tenant deployment — enough to land a
design partner while Phase 2 multi-tenancy is built.

---

## Effort & risk notes
- **Highest leverage / lowest risk:** audit log, Alertmanager adapter, secrets store, HA.
- **Biggest lift:** multi-tenancy (touches every model/query) and SOC 2 (process + time, not just code).
- **Most important to get right:** automation safety — the difference between "helpful" and "caused an outage." Keep approvals mandatory until guardrails + track record justify otherwise.
