from pydantic import BaseModel, EmailStr, Field, ConfigDict # type: ignore
from typing import Optional

# INPUT: Data sent TO the API
class CarbonDataInput(BaseModel):
    sku_name: str
    category: str
    region: str
    vendor: str
    raw_material_energy: float
    raw_material_emission_factor: float
    raw_material_waste: float
    manufacturing_energy: float
    manufacturing_efficiency: float
    manufacturing_water_usage: float
    transport_distance_km: float
    transport_mode_factor: float
    logistics_energy: float
    usage_energy_consumption: float
    usage_duration_hours: float
    grid_carbon_intensity: float
    recycling_efficiency: float
    disposal_emission_factor: float
    recovered_material_value: float
    state_complexity_index: float
    policy_action_score: float
    optimization_reward_signal: float

    model_config = ConfigDict(protected_namespaces=())

# OUTPUT: Data sent FROM the API
class PredictionOutput(BaseModel):
    predicted_carbon_footprint: float
    confidence_interval: list[float]
    anomaly_detected: bool
    model_version: str
    metadata: dict

    model_config = ConfigDict(protected_namespaces=())

class SustainabilityMetrics(BaseModel):
    total_co2: float
    avg_intensity: float
    renewable_mix: float
    active_nodes: int
    compliance_score: str
    region_breakdown: dict
    timestamp: str

class IngestionResponse(BaseModel):
    status: str
    records_added: int
    data_hash: str
    audit_id: str
    verification_chain: str

class ForecastOutput(BaseModel):
    period: str
    baseline_projection: list[float]
    optimistic_projection: list[float]
    pessimistic_projection: list[float]
    confidence_score: float
    methodology: str

class TrendOutput(BaseModel):
    category_trends: dict
    vendor_performance: dict
    yoy_change: float


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "viewer" # viewer, editor, admin

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

# SUSTAINABILITY ACTIONS
class RecommendationAction(BaseModel):
    id: str
    action: str
    impact_score: float  # 0 to 1
    savings_est_kg: float
    complexity: str  # "Low", "Medium", "High"
    category: str

class RecommendationOutput(BaseModel):
    recommendations: list[RecommendationAction]
    overall_sustainability_index: float
    timestamp: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None