import asyncio
import logging
import hashlib
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import SessionLocal, Ledger, AuditLog, get_latest_hash
from app.ledger_engine import MerkleTree, calculate_audit_signature
from app.ml_ops import DriftDetector, RetrainingManager
from app.ml_engine import MLEngine
import pandas as pd

logger = logging.getLogger("EcoTrack-Ingestion")

class IngestionSystem:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False

    async def producer(self, records: list, username: str):
        """ Adds records to the high-throughput ingestion queue. """
        batch_id = str(uuid.uuid4().hex[:8]).upper()
        await self.queue.put({
            "batch_id": batch_id,
            "records": records,
            "username": username,
            "received_at": datetime.now()
        })
        return batch_id

    async def stream_worker(self):
        """ Background consumer that processes telemetry batches. """
        self.is_running = True
        logger.info("🚀 Stream Worker Activated: Monitoring Ingestion Queue...")
        
        while self.is_running:
            try:
                job = await self.queue.get()
                batch_id = str(job["batch_id"])
                records = list(job["records"]) # type: ignore
                username = str(job["username"])
                
                logger.info(f"📦 Processing Batch {batch_id} ({len(records)} records)...")
                
                db = SessionLocal()
                try:
                    await self._process_batch(db, records, batch_id, username)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"❌ Batch {batch_id} Processing Error: {e}")
                finally:
                    db.close()
                    self.queue.task_done()
                    
            except Exception as e:
                logger.error(f"Stream Worker Critical Error: {e}")
                await asyncio.sleep(1)

    async def _process_batch(self, db: Session, data: list, batch_id: str, operator: str):
        """ Core batch processing logic (Ledger + Merkle + MLOps). """
        prev_hash = get_latest_hash(db)
        batch_hashes = []
        ingested_data_list = []
        
        for record in data:
            u_hex = uuid.uuid4().hex
            product_id = "SKU-" + str(u_hex[0:5]).upper() # type: ignore
            timestamp = datetime.now()
            
            # Emission factors: 0.45 kg CO2/kWh for raw materials, 0.65 kg CO2/kWh for manufacturing
            total_carbon = (record["raw_material_energy"] * 0.45) + (record["manufacturing_energy"] * 0.65)
            
            # Chaining
            payload = f"{timestamp.isoformat()}|{record['sku_name']}|{total_carbon}|{prev_hash}"
            record_hash = hashlib.sha256(payload.encode()).hexdigest()
            
            new_record = Ledger(
                timestamp=timestamp,
                product_id=product_id,
                sku_name=record["sku_name"],
                category=record["category"],
                region=record["region"],
                vendor=record["vendor"],
                total_lifecycle_carbon_footprint=float(round(total_carbon, 2)),
                hash=record_hash,
                prev_hash=prev_hash,
                is_anomaly=0
            )
            db.add(new_record)
            
            ingested_data_list.append({**record, "total_lifecycle_carbon_footprint": total_carbon})
            batch_hashes.append(record_hash)
            prev_hash = record_hash

        # Merkle Tree anchoring
        tree = MerkleTree(batch_hashes)
        merkle_root = tree.get_root()
        now_ts = datetime.now()
        signature = calculate_audit_signature(merkle_root, now_ts.isoformat())
        
        audit_entry = AuditLog(
            batch_id=batch_id,
            record_count=len(data),
            merkle_root=merkle_root,
            signature=signature,
            operator=operator,
            timestamp=now_ts
        )
        db.add(audit_entry)

        # MLOps Drift Check
        try:
            drift_detector = DriftDetector()
            if drift_detector.check_drift(pd.DataFrame(ingested_data_list)):
                retrain_manager = RetrainingManager(MLEngine())
                retrain_manager.trigger_retraining(pd.DataFrame(ingested_data_list), "total_lifecycle_carbon_footprint")
        except Exception as e:
            logger.warning(f"MLOps Bypass in Stream Worker: {e}")

# Global Singleton Ingestion Engine
ingestion_engine = IngestionSystem()
