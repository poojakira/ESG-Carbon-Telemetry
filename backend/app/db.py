import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Ledger(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    product_id = Column(String, index=True)
    sku_name = Column(String, index=True)
    category = Column(String, index=True)
    region = Column(String, index=True)
    vendor = Column(String, index=True)
    total_lifecycle_carbon_footprint = Column(Float)
    hash = Column(String, unique=True)
    prev_hash = Column(String)
    is_anomaly = Column(Integer, default=0)

    # Time-series Optimization: Composite Index for fast filtering
    __table_args__ = (
        Index('ix_ledger_timestamp_sku', "timestamp", "sku_name"),
        Index('ix_ledger_vendor_category', "vendor", "category"),
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer") # viewer, editor, admin
    is_active = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    batch_id = Column(String, unique=True, index=True)
    record_count = Column(Integer)
    merkle_root = Column(String)
    signature = Column(String) # Simulated digital signature
    operator = Column(String)  # The user who performed ingestion


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_latest_hash(db: SessionLocal):
    row = db.query(Ledger).order_by(Ledger.id.desc()).first()
    return row.hash if row else "0" * 64


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seeding (Enterprise approach: only if empty)
    db = SessionLocal()
    try:
        if db.query(Ledger).count() == 0 and os.path.exists(settings.DATA_PATH):
            df = pd.read_csv(settings.DATA_PATH)
            carbon_col = 'total_lifecycle_carbon_footprint'
            
            # Absolute Reality: Direct Column Mapping
            records = []
            for _, row in df.iterrows():
                # Convert string timestamp to datetime if necessary
                ts = row['Timestamp']
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except ValueError:
                        ts = datetime.utcnow() # Fallback

                records.append(Ledger(
                    timestamp=ts,
                    product_id=str(row['Product_ID']),
                    sku_name=str(row['SKU_Name']),
                    category=str(row['Category']),
                    region=str(row['Region']),
                    vendor=str(row['Vendor']),
                    total_lifecycle_carbon_footprint=float(row[carbon_col]),
                    hash=str(row['Hash']),
                    prev_hash=str(row['Prev_Hash']),
                    is_anomaly=0
                ))
            
            db.bulk_save_objects(records)
            db.commit()
            print(f"📦 Database seeded with {len(records)} records from CSV.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
