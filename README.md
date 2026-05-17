# carbon-analytics-platform

FastAPI backend for carbon emissions tracking with async ingestion, Merkle audit trail, and time-series forecasting.

## What This Is

A REST API that ingests carbon emission records, stores them in PostgreSQL with a hash-chain audit trail, and serves forecasts via an ARIMA ensemble. Streamlit frontend for visualization.

## What's Real

- **FastAPI + SQLAlchemy + PostgreSQL** — real CRUD with Pydantic validation, JWT auth, RBAC
- **Merkle hash chain** — each batch of ingested records gets a SHA-256 chain + Merkle root. Provides integrity verification (can detect if records were modified after insertion)
- **ARIMA forecast** — 0.7 × ARIMA(1,1,1) + 0.3 × linear trend. No validation set, no published MAE.
- **Async ingestion** — `asyncio.Queue` consumer processes batches in background

## What's NOT Real

- **The Merkle chain is single-process.** Two replicas = two divergent chains. No consensus, no shared state. The "audit trail" only works on a single instance.
- **The "signature" is a keyed hash with a dev-default key.** `os.getenv('LEDGER_SIGNING_KEY', 'dev-only-key')` — not cryptographic signing. Anyone with env access can forge.
- **No benchmark script exists.** Previously published numbers (42ms p99, 13.6x verification speed) were not produced by any code in this repo. They've been removed.
- **Coverage badge was decorative.** No `pytest --cov` in CI. No coverage report generated.
- **The forecast has no validation.** ARIMA is fit on all available data with no train/test split. The "4.2% MAE" number had no source.

## Running

```bash
cd backend
pip install -r requirements.txt
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
export DATABASE_URL=sqlite:///./dev.db
uvicorn app.main:app --reload
# http://localhost:8000/docs
```

With Docker:
```bash
export POSTGRES_PASSWORD=localdev
export SECRET_KEY=dev-secret
docker compose up
```

## Known Issues

- **Double-except bug in main.py** — two consecutive `except Exception` blocks on the ingest endpoint. Second is unreachable. `db.rollback()` never fires on errors.
- **eco/ directory is dead code.** `eco/pipeline/async_ingest.py` and `eco/audit/merkle_trail.py` are standalone reference implementations never imported by the backend.
- **Model files committed to git.** `backend/data/model.pkl` and `security_model.pkl` are opaque pickles with no training script. They exist so the API has something to load at startup.
- **SQLite pool_size removed.** Was originally set to 20 (incompatible with SQLite). Fixed.
- **Frontend is one file.** `frontend/dashboard.py` (271 lines) is the entire "Intelligence Layer."

## Development Notes

**The missing database service.** `docker-compose.yml` originally referenced `@db:5432` in DATABASE_URL but defined no PostgreSQL service. The backend crashed on startup with `ConnectionRefusedError`. Added a proper `db` service with env var interpolation and volume persistence.

**Hardcoded secrets in source.** `backend/config/production.yaml` and `.env.production` both had plaintext passwords committed to git. Replaced with `${VAR}` placeholders and documented that secrets must come from a secret manager.

**The emission factor magic numbers.** `ingestion_engine.py` uses `0.45` and `0.65` as carbon intensity coefficients. These represent kg CO2/kWh for raw material processing and manufacturing respectively (EPA emission factors for US grid average). Now documented in-line.

## Structure

```
backend/
  app/
    main.py          — FastAPI app, routes, lifespan
    auth.py          — JWT + bcrypt
    db.py            — SQLAlchemy models + session
    ingestion_engine.py — Async batch consumer
    ledger_engine.py — Merkle hash chain
    ml_engine.py     — XGBoost + ARIMA (XGBoost is dead code)
  data/              — SQLite DB + pickled models (should not be in git)
frontend/
  dashboard.py       — Streamlit visualization
```

## Author

Pooja Kiran — [@poojakira](https://github.com/poojakira)
