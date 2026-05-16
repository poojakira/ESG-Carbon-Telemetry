import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
import os
import sys
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ML-Factory")

# Ensure we can import from app
sys.path.append(os.getcwd())
from app.config import settings

class ModelFactory:
    """Pluggable model factory to satisfy README claims of a flexible ML pipeline."""
    @staticmethod
    def get_regressor(model_type="random_forest"):
        if model_type == "random_forest":
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            return GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

def train(model_type="random_forest"):
    logger.info(f"STARTING TRAINING (Policy: {model_type})...")

    # 1. Load Data
    if not os.path.exists(settings.DATA_PATH):
        logger.error(f"❌ CRITICAL: Data file not found at {settings.DATA_PATH}")
        return

    df = pd.read_csv(settings.DATA_PATH)
    
    # 2. Define Features (MUST match app/schemas.py)
    features = [
        "raw_material_energy", "raw_material_emission_factor", "raw_material_waste",
        "manufacturing_energy", "manufacturing_efficiency", "manufacturing_water_usage",
        "transport_distance_km", "transport_mode_factor", "logistics_energy",
        "usage_energy_consumption", "usage_duration_hours", "grid_carbon_intensity",
        "recycling_efficiency", "disposal_emission_factor", "recovered_material_value",
        "state_complexity_index", "policy_action_score", "optimization_reward_signal"
    ]
    target = "total_lifecycle_carbon_footprint"

    X = df[features]
    y = df[target]

    # 3. Train Business Model via Factory
    logger.info(f"🧠 Training {model_type} regressor...")
    regressor = ModelFactory.get_regressor(model_type)
    regressor.fit(X, y)
    
    # Measure R2
    from sklearn.metrics import r2_score
    r2 = r2_score(y, regressor.predict(X))
    logger.info(f"📊 Model Fidelity (R^2): {r2:.4f}")
    
    joblib.dump(regressor, settings.MODEL_PATH)
    logger.info(f"✅ Saved Business Model to: {settings.MODEL_PATH}")

    # 4. Train Security Model
    logger.info("🛡️  Training Anomaly Guard (Isolation Forest)...")
    security_model = IsolationForest(contamination=0.03, random_state=42)
    security_model.fit(X)
    
    joblib.dump(security_model, settings.SECURITY_PATH)
    logger.info(f"✅ Saved Security Model to: {settings.SECURITY_PATH}")

    logger.info("TRAINING COMPLETE.")

if __name__ == "__main__":
    # Allow model type selection via CLI or default to random_forest
    model_choice = sys.argv[1] if len(sys.argv) > 1 else "random_forest"
    train(model_choice)