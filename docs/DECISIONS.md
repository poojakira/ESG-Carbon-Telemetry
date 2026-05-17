# Architectural Decisions

## FastAPI over Flask

Chose FastAPI over Flask because async batch ingestion was a requirement from day one. Flask's WSGI model would need Celery for background tasks — too many moving parts.

## PostgreSQL over SQLite

Needed concurrent writes from multiple ingestion workers. SQLite's write lock would serialize everything.

## ARIMA for forecasting instead of Prophet

Prophet's install is 200MB+ and pulls in Stan. ARIMA from statsmodels is lighter and good enough for monthly carbon data with clear seasonality.

## Merkle hash-chain for audit

Regulatory requirement for ESG reporting is tamper-evidence. Considered blockchain (Hyperledger) but that's absurd for a single-org audit trail. A hash chain with Merkle root gives the same tamper-detection guarantee without consensus overhead.

## Batch ingestion (async queue + periodic flush)

Instead of row-by-row inserts: PostgreSQL COPY is 10-50x faster than individual INSERTs for bulk data. Queue accumulates records, flushes every 5 seconds or 1000 records (whichever comes first).

## Plain PostgreSQL over TimescaleDB

Tried TimescaleDB extension for time-series queries — worked great but added deployment complexity. Plain PostgreSQL with date-range partitioning is simpler and fast enough for the data volume (<1M rows/month).

## Streamlit dashboard

Last-minute addition for demos. It's not production-grade — no auth, no caching, re-runs queries on every interaction. Fine for internal use.
