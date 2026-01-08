# Backend Local Setup

This document describes the minimal steps to run the backend API locally using a Python virtual environment.

Prerequisites
- Python 3.11+ (Python 3.14 was used for initial development)
- Homebrew (macOS) if you need to install `libpq` for `psycopg2` builds

Steps

1. Create a virtual environment

```bash
python3 -m venv backend/.venv
```

2. Upgrade packaging tools inside the venv

```bash
backend/.venv/bin/python -m pip install --upgrade pip setuptools wheel
```

3. Install minimal development dependencies

We provide a small `requirements.dev.txt` for local development to avoid heavy optional packages.

```bash
backend/.venv/bin/pip install -r backend/requirements.dev.txt
```

4. Start the backend server

Run the following from the project root or change into the `backend/` folder first.

```bash
# from repo root
cd backend
./.venv/bin/uvicorn app.main:app --reload --port 8001 --host 127.0.0.1
```

5. Verify the health endpoint

Open your browser or run curl:

```bash
curl http://127.0.0.1:8001/health
# Expected response: {"status":"ok","version":"0.1.0"}
```

Troubleshooting
- If installation fails while building `psycopg2` with an error about `pg_config`, install libpq via Homebrew:

```bash
brew install libpq
# Then ensure pg_config is on your PATH in this shell:
export PATH="$(brew --prefix libpq)/bin:$PATH"
```

- If you want to install the full `backend/requirements.txt` and encounter package resolution issues (for example `langgraph` pinned to an unavailable version), consider:
  - Removing or relaxing problematic pinned versions temporarily, or
  - Installing only `requirements.dev.txt` for local development and adding full dependencies in CI or in a dedicated environment.

Notes
- `requirements.dev.txt` contains the minimal packages needed to run the API locally (FastAPI + Uvicorn + python-dotenv).
- This document is intended as a quickstart. For production, follow the `Dockerfile` and `infra/` terraform manifests.

If you want, I can add a small `backend/run.sh` script that wraps these commands and make it executable.
