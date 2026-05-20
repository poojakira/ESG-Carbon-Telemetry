# carbon-analytics-platform

> Async data pipeline: high-throughput batch ingestion (PostgreSQL COPY), ARIMA time-series forecasting, cryptographic audit trail. Demonstrates patterns for any industrial telemetry backend.

FastAPI backend for carbon emissions tracking with async ingestion, Merkle audit trail, and time-series forecasting.

## API

```
POST /ingest          — Batch insert emission records (async queue, flushes every 5s or 1000 records)
GET  /emissions       — Query emissions by date range, facility, scope
GET  /forecast        — ARIMA forecast for next N periods
GET  /audit/verify    — Verify Merkle hash-chain integrity
GET  /audit/root      — Current Merkle root hash
GET  /health          — Service health + DB connection status
```

All endpoints return JSON. Auth is API-key based (header: `X-API-Key`).

## Quick start

```bash
docker-compose up -d          # starts PostgreSQL + API
curl -X POST localhost:8000/ingest -H 'Content-Type: application/json' -d @sample_data.json
curl localhost:8000/emissions?start=2024-01-01&end=2024-12-31
```

## Stack

- FastAPI + uvicorn (async)
- PostgreSQL (emissions storage, date-range partitioned)
- ARIMA via statsmodels (forecasting)
- SHA-256 hash chain with Merkle root (audit trail)

## Design decisions

Batch ingestion uses an async queue that flushes to PostgreSQL via COPY (10-50x faster than row-by-row INSERT). The Merkle chain is single-process — two replicas would produce divergent chains. This is a single-org audit tool, not a distributed ledger.

ARIMA was chosen over Prophet because Prophet pulls in Stan (200MB+). For monthly data with clear seasonality, ARIMA is sufficient.

See `docs/DECISIONS.md` for full architectural rationale.
