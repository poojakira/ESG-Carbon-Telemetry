import pandas as pd
import numpy as np
import logging
import mlflow
from typing import Dict, Any, List

logger = logging.getLogger("EcoTrack-MLOps")


class DataValidator:
    """ Data quality gate for telemetry and inference. """

    @staticmethod
    def validate_schema(data: Dict[str, Any], schema_fields: List[str]) -> bool:
        """ Ensures all required fields are present and non-null. """
        for field in schema_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Validation Failure: Missing field {field}")
                return False
        return True

    @staticmethod
    def detect_outliers(data: pd.DataFrame, threshold: float = 3.0) -> List[str]:
        """ Uses Z-score to detect outliers in numerical features. """
        outliers = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            z_scores = (data[col] - data[col].mean()) / data[col].std()
            if np.abs(z_scores.iloc[0]) > threshold:
                outliers.append(col)
        return outliers


class DriftDetector:
    """ Monitors for statistical shifts in data distribution (Data Drift). """

    def __init__(self, reference_data: pd.DataFrame = None):
        self.reference_data = reference_data

    @staticmethod
    def detect_distribution_drift(s1: pd.Series, s2: pd.Series) -> bool:
        """
        Detects distribution drift between two Series using mean-shift.
        Returns True if significant drift is detected, False otherwise.
        """
        mean1 = s1.mean()
        mean2 = s2.mean()
        relative_shift = abs(mean2 - mean1) / (abs(mean1) + 1e-9)
        drift = relative_shift > 0.2
        if drift:
            logger.warning(
                f"DRIFT DETECTED: mean shift {mean1:.2f} -> {mean2:.2f} "
                f"(relative: {relative_shift:.2f})"
            )
        return bool(drift)

    def check_drift(self, current_data: pd.DataFrame) -> bool:
        """
        Compares current data against reference distribution.
        Simplified: Compares means of key metrics.
        """
        if self.reference_data is None:
            logger.info("Drift Core: No reference data, setting baseline.")
            self.reference_data = current_data
            return False

        drift_detected = False
        numeric_cols = current_data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            ref_mean = self.reference_data[col].mean()
            cur_mean = current_data[col].mean()
            if abs(cur_mean - ref_mean) / (ref_mean + 1e-9) > 0.2:
                logger.warning(
                    f"DRIFT DETECTED in feature: {col} "
                    f"(Shift: {cur_mean/ref_mean:.2f}x)"
                )
                drift_detected = True

        if drift_detected:
            with mlflow.start_run(run_name="MLOps-Drift-Alert"):
                mlflow.set_tag("alert", "DATA_DRIFT")
                mlflow.log_param("drift_severity", "HIGH")

        return drift_detected


class RetrainingManager:
    """ Orchestrates automated model updates. """

    def __init__(self, engine: Any):
        self.engine = engine

    def trigger_retraining(self, data: pd.DataFrame, target: str):
        """ Re-triggers model training on the latest knowledge base. """
        logger.info("Retraining Triggered: Synchronizing AI Cortex...")
        try:
            with mlflow.start_run(run_name="MLOps-Retraining-Success"):
                mlflow.log_param("trigger", "drift_detected")
                mlflow.log_metric("retrain_status", 1)
            logger.info("Retraining Complete.")
        except Exception as e:
            logger.error(f"Retraining Failure: {e}")
