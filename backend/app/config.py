from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
from typing import Optional, Dict, Any
import os
import yaml


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_prefix="", case_sensitive=False)

    # Core Infrastructure
    PROJECT_NAME: str = "Carbon Analytics"
    VERSION: str = "8.5.0-STABLE"
    ENV: str = os.getenv("ENV", "development")

    # DATABASE & SECURITY
    DATABASE_URL: str = "sqlite:///./ecotrack_enterprise.db"
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ML & TELEMETRY
    MODEL_PATH: str = "data/model.pkl"
    SECURITY_PATH: str = "data/security_model.pkl"

    # OBSERVABILITY
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_METRICS: bool = True

    @classmethod
    def load_from_yaml(cls) -> "Settings":
        """ Hybrid YAML + ENV loader for industrial deployments. """
        env = os.getenv("ENV", "development")
        config_dir = "config"

        # Load Base
        with open(os.path.join(config_dir, "base.yaml"), "r") as f:
            base_cfg = yaml.safe_load(f)

        # Load Env Overrides
        env_file = os.path.join(config_dir, f"{env}.yaml")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                env_cfg = yaml.safe_load(f)
            base_cfg.update(env_cfg)

        # Merge into Settings (ENV vars always win)
        return cls(**base_cfg)


# Initialize Industrial Settings
settings = Settings.load_from_yaml()
