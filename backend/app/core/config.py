import json
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project Info
    PROJECT_NAME: str = "GreenOps FinOps & Carbon Budget Gatekeeper"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./greenops.db"

    # Security & GitHub
    GITHUB_WEBHOOK_SECRET: str = "demo_webhook_secret_for_development_32_chars"
    GITHUB_TOKEN: str = "ghp_dummy_token_for_testing"
    GITHUB_APP_ID: str = ""
    GITHUB_PRIVATE_KEY: str = ""

    # Electricity Maps API
    ELECTRICITY_MAPS_API_KEY: str = "mock_electricity_maps_key"
    DEFAULT_GRID_REGION: str = "US-EAST"
    GRID_CACHE_TTL_MINUTES: int = 60

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v


settings = Settings()
