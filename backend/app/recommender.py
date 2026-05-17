import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import uuid
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class SustainabilityAction:
    """Represents a single sustainability optimization action."""
    action_id: str
    category: str
    action_description: str
    impact_score: float
    savings_est_kg: float
    complexity: str


@dataclass
class SustainabilityPlan:
    """Holds a full set of sustainability recommendations."""
    actions: List[SustainabilityAction]
    total_optimization_potential: float
    generated_at: str


class RecommenderEngine:
    """
    Industrial Sustainability Recommendation Engine.
    Uses multi-criteria optimization to suggest carbon reduction actions.
    """

    def __init__(self):
        self.categories = ["Energy", "Supply Chain", "Materials", "Logistics"]

    def generate_recommendations(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ Analyzes metrics and suggests high-impact actions. """
        recommendations = []

        # 1. Energy Optimization Logic
        if current_metrics.get("avg_intensity", 0) > 400:
            recommendations.append({
                "id": str(uuid.uuid4())[:8],  # type: ignore
                "action": "Shift high-energy operations to night-shift (Grid mix: -15% CO2)",
                "impact_score": 0.85,
                "savings_est_kg": round(current_metrics["avg_intensity"] * 0.15, 2),
                "complexity": "Low",
                "category": "Energy"
            })
        # 2. Material Efficiency
        recommendations.append({
            "id": str(uuid.uuid4())[:8],
            "action": "Switch to Bio-Polymer for product line (Recyclability: +40%)",
            "impact_score": 0.72,
            "savings_est_kg": 12.5,
            "complexity": "Medium",
            "category": "Materials"
        })
        # 3. Supply Chain / Logistics
        if "region_breakdown" in current_metrics:
            highest_region = max(
                current_metrics["region_breakdown"],
                key=current_metrics["region_breakdown"].get  # type: ignore
            )
            recommendations.append({
                "id": str(uuid.uuid4())[:8],
                "action": f"Localize assembly in {highest_region} to reduce air-freight",
                "impact_score": 0.92,
                "savings_est_kg": 45.0,
                "complexity": "High",
                "category": "Supply Chain"
            })
        return recommendations

    def calculate_sustainability_index(self, metrics: Dict[str, Any]) -> float:
        """ Returns a normalized 0-100 score of current health. """
        intensity = metrics.get("avg_intensity", 500)
        score = max(0, min(100, 100 - (intensity / 10)))
        return round(score, 1)

    def _generate_supply_chain_action(
        self, transport_distance: float, carbon_footprint: float
    ) -> SustainabilityAction:
        """
        Generates a supply chain optimization action based on transport distance
        and carbon footprint values.
        """
        impact = round((transport_distance / 100.0) * (carbon_footprint / 100.0), 2)
        return SustainabilityAction(
            action_id=str(uuid.uuid4())[:8],
            category="Supply Chain",
            action_description="Switch to low-carbon logistics provider to reduce transport emissions",
            impact_score=impact,
            savings_est_kg=round(carbon_footprint * 0.15, 2),
            complexity="Medium",
        )

    def optimize_sustainability(self, historical_data: List[Dict[str, Any]]) -> SustainabilityPlan:
        """
        Analyzes historical data records and produces a full sustainability
        optimization plan with scored actions.
        """
        actions: List[SustainabilityAction] = []
        total_potential = 0.0

        for record in historical_data:
            carbon = record.get("carbon_footprint", 0.0)
            transport = record.get("transport_distance_km", 0.0)
            raw_energy = record.get("raw_material_energy", 0.0)
            mfg_energy = record.get("manufacturing_energy", 0.0)

            # Supply chain action
            if transport > 0 and carbon > 0:
                sc_action = self._generate_supply_chain_action(transport, carbon)
                actions.append(sc_action)
                total_potential += sc_action.impact_score

            # Energy action
            if raw_energy + mfg_energy > 0:
                energy_impact = round((raw_energy + mfg_energy) * 0.1, 2)
                actions.append(SustainabilityAction(
                    action_id=str(uuid.uuid4())[:8],
                    category="Energy",
                    action_description="Optimize manufacturing energy mix with renewables",
                    impact_score=energy_impact,
                    savings_est_kg=round(carbon * 0.1, 2),
                    complexity="Low",
                ))
                total_potential += energy_impact

        return SustainabilityPlan(
            actions=actions,
            total_optimization_potential=round(total_potential, 2),
            generated_at=datetime.now().isoformat(),
        )


recommender = RecommenderEngine()
