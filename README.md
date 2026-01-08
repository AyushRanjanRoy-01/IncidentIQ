# AI-SRE Platform

Production-grade AI-powered Site Reliability Engineering platform that automates incident detection, root cause analysis, and self-healing remediation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Ingestion Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Prometheus│  │   Loki   │  │  OTel    │  │  Kafka   │      │
│  │ Metrics  │  │  Logs    │  │ Traces   │  │  Events  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │      AI Intelligence Core            │
        │  ┌──────────┐  ┌──────────┐        │
        │  │ Anomaly  │  │  Alert   │        │
        │  │Detection │  │Correlation│        │
        │  └────┬─────┘  └────┬─────┘        │
        │       │              │              │
        │       └──────┬───────┘              │
        │              ▼                      │
        │     ┌─────────────────┐             │
        │     │ Multi-Agent     │             │
        │     │ Orchestration   │             │
        │     └────────┬────────┘             │
        │              │                      │
        │              ▼                      │
        │     ┌─────────────────┐             │
        │     │  RAG Knowledge  │             │
        │     │    Retrieval    │             │
        │     └────────┬────────┘             │
        └──────────────┼──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │      Functional Features             │
        │  ┌──────────┐  ┌──────────┐        │
        │  │Automated │  │Predictive │        │
        │  │   RCA    │  │ Planning  │        │
        │  └────┬─────┘  └────┬─────┘        │
        │       │              │              │
        │       └──────┬───────┘              │
        │              ▼                      │
        │     ┌─────────────────┐             │
        │     │ Self-Healing    │             │
        │     │    Actions      │             │
        │     └────────┬────────┘             │
        └──────────────┼──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │      Action & Feedback                │
        │  ┌──────────┐  ┌──────────┐        │
        │  │ ChatOps  │  │Infrastructure│     │
        │  │(Slack/PD)│  │(K8s/Terraform)│    │
        │  └────┬─────┘  └────┬─────┘        │
        │       │              │              │
        │       └──────┬───────┘              │
        │              ▼                      │
        │     ┌─────────────────┐             │
        │     │ Human Approval   │             │
        │     │   (HITL)         │             │
        │     └─────────────────┘             │
        └─────────────────────────────────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Python 3.12+** - Latest Python features
- **SQLAlchemy 2.0** - Modern ORM with async support
- **PostgreSQL + pgvector** - Vector database for RAG
- **Redis** - Caching and pub/sub
- **Dramatiq** - Modern async task queue (replaces Celery)
- **LangGraph** - Multi-agent orchestration
- **OpenTelemetry** - Unified observability
- **structlog** - Structured logging

### Frontend
- **React 18+** - UI library
- **TypeScript 5+** - Type safety
- **Vite** - Build tool
- **Tailwind CSS v4** - Styling
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Zod** - Runtime validation

### Infrastructure
- **Terraform** - Infrastructure as Code
- **Kubernetes** - Container orchestration
- **Helm** - K8s package management
- **ArgoCD** - GitOps deployment
- **Docker** - Containerization
- **Prometheus + Grafana** - Monitoring
- **OpenTelemetry Collector** - Observability pipeline

### AI/ML
- **OpenAI/Anthropic** - LLM providers
- **LangSmith/LangFuse** - LLM observability
- **scikit-learn** - Anomaly detection
- **Prophet** - Time-series forecasting
- **sentence-transformers** - Embeddings

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### Local Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd IncidentIQ
   ```

2. **Setup environment**
   ```bash
   make setup-local
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start services**
   ```bash
   make docker-up
   ```

5. **Run migrations**
   ```bash
   make migrate
   ```

6. **Start development servers**
   ```bash
   # Terminal 1: Backend
   make run-backend

   # Terminal 2: Frontend
   make run-frontend

   # Terminal 3: Workers
   make run-workers
   ```

7. **Access services**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001
   - Prometheus: http://localhost:9090

## Project Structure

```
ai-sre-platform/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── agents/   # Multi-agent system
│   │   ├── ml/       # ML models
│   │   ├── rag/      # RAG pipeline
│   │   ├── services/ # Business logic
│   │   ├── security/ # Auth & security
│   │   ├── events/   # Event-driven architecture
│   │   └── cost/     # Cost tracking
│   └── tests/        # Test suite
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── hooks/
├── infra/            # Infrastructure
│   ├── terraform/    # IaC
│   ├── kubernetes/   # K8s manifests
│   └── helm/        # Helm charts
├── monitoring/       # Observability configs
└── scripts/         # Utility scripts
```

## Key Features

### 🤖 Multi-Agent System
- **Supervisor Agent**: Orchestrates specialist agents
- **Triage Agent**: Filters noise and duplicates
- **Context Agent**: Gathers logs, metrics, events
- **Knowledge Agent**: RAG search through runbooks
- **RCA Agent**: Synthesizes root cause analysis

### 🔍 Automated RCA
- AI-powered root cause analysis
- Confidence scoring
- Evidence-based recommendations
- Historical incident correlation

### 🛠️ Self-Healing
- Automated remediation actions
- Human-in-the-loop approval
- Rollback capabilities
- Action logging and auditing

### 📊 Observability
- OpenTelemetry traces, metrics, logs
- Real-time dashboards
- Cost tracking (LLM + infrastructure)
- Alert correlation

### 🔐 Security
- JWT authentication
- Vault secret management
- Rate limiting
- Input validation
- RBAC

## Development

### Running Tests
```bash
make test              # All tests
make test-backend      # Backend only
make test-frontend     # Frontend only
```

### Linting & Formatting
```bash
make lint              # Check code quality
make format            # Auto-format code
```

### Database Migrations
```bash
make migrate                    # Run migrations
make migrate-create MESSAGE="..."  # Create migration
```

## Deployment

### Development
```bash
make deploy-dev
```

### Production
```bash
make deploy-prod  # Requires confirmation
```

## Documentation

- [Architecture](./docs/architecture.md)
- [Agent Workflows](./docs/agent_workflows.md)
- [Deployment Guide](./docs/deployment.md)
- [API Documentation](./docs/api/openapi.yaml)
- [Security Best Practices](./docs/security.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
