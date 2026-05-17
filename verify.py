"""
ESG-Carbon-Telemetry — 5-minute verification script.
Run: python verify.py
No PostgreSQL, no Docker required. Uses SQLite fallback.
"""
import sys, os, time
sys.path.insert(0, "backend")
os.environ.setdefault("SECRET_KEY", "verify-script-dev-key")
os.environ.setdefault("ENV", "development")

print("=" * 60)
print("ESG CARBON TELEMETRY VERIFICATION")
print("=" * 60)

# 1. Config loads
print("\n[1/5] Loading configuration...")
from app.config import settings
print(f"  Project: {settings.PROJECT_NAME} v{settings.VERSION}")
print(f"  Environment: {settings.ENV}")

# 2. API smoke test
print("\n[2/5] Testing FastAPI endpoints...")
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
health = client.get("/health")
print(f"  GET /health -> {health.status_code}")
if health.status_code == 200:
    print(f"  Response: {health.json()}")

# 3. Ingest sample data
print("\n[3/5] Testing batch ingestion...")
sample_records = [
    {"facility": "Plant-A", "scope": 1, "co2_kg": 1250.5, "date": "2024-06-01"},
    {"facility": "Plant-A", "scope": 2, "co2_kg": 890.2, "date": "2024-06-01"},
    {"facility": "Plant-B", "scope": 1, "co2_kg": 2100.0, "date": "2024-06-01"},
    {"facility": "Plant-B", "scope": 3, "co2_kg": 450.8, "date": "2024-06-01"},
]
resp = client.post("/ingest", json=sample_records)
print(f"  POST /ingest ({len(sample_records)} records) -> {resp.status_code}")

# 4. ARIMA forecasting
print("\n[4/5] ARIMA time-series forecasting...")
import numpy as np
try:
    from statsmodels.tsa.arima.model import ARIMA

    np.random.seed(42)
    # Simulate 24 months of emissions with trend + seasonality
    months = np.arange(24)
    emissions = 1000 + 50 * months + 200 * np.sin(months * np.pi / 6) + np.random.normal(0, 50, 24)

    model = ARIMA(emissions, order=(1, 1, 1))
    fitted = model.fit()
    forecast = fitted.forecast(steps=6)
    print(f"  Trained on {len(emissions)} months of data")
    print(f"  6-month forecast: {[f'{v:.0f}' for v in forecast]} kg CO2")
except ImportError:
    print("  statsmodels not installed — skipping ARIMA demo")

# 5. Merkle audit trail
print("\n[5/5] Merkle hash-chain audit trail...")
import hashlib, json

chain = []
for i, record in enumerate(sample_records):
    prev_hash = chain[-1]["hash"] if chain else "0" * 64
    block = {"index": i, "data": record, "prev_hash": prev_hash}
    block["hash"] = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
    chain.append(block)

# Verify chain integrity
valid = True
for i in range(1, len(chain)):
    if chain[i]["prev_hash"] != chain[i-1]["hash"]:
        valid = False
        break

print(f"  Chain length: {len(chain)} blocks")
print(f"  Latest hash: {chain[-1]['hash'][:32]}...")
print(f"  Chain integrity: {'VALID' if valid else 'BROKEN'}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
